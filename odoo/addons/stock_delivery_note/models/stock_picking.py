# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from collections import defaultdict
from datetime import datetime
from io import BytesIO

import unicodecsv as csv
from odoo import api, models
from odoo.tools import config
from unidecode import unidecode


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_transfer(self):
        to_do = self.filtered(lambda p: p.state not in ("cancel", "done"))
        if not to_do:
            return True
        result = super(StockPicking, to_do).do_transfer()
        picking_type_out = self.env.ref("stock.picking_type_out")
        if self.env.context.get("skip_pdf_gen"):
            return result
        for r in to_do:
            if r.picking_type_id == picking_type_out:
                r._send_delivery_notes(
                    r.customer_id.send_csv_deliveryship,
                    r.customer_id.send_pdf_deliveryship,
                )
        return result

    @api.multi
    def _get_delivery_note_filename(self, extension):
        """Return the delivery note filename."""
        self.ensure_one()
        if not self.date_done:
            return
        sale_orders = self.move_lines.mapped("order_id")

        return (
            "_".join(
                [
                    "NE",
                    sale_orders[0].partner_id.ref or "" if len(sale_orders) else "",
                    str(self.id),
                    "".join(self.date_done[:10].split("-")),
                    "".join(self.date_done[-8:].split(":")),
                ]
            )
            + extension
        )

    @api.multi
    def _generate_delivery_note_csv(self):
        """Save the delivery note in csv format in ir.attachment"""
        self.ensure_one()
        filename = self._get_delivery_note_filename(extension=".csv")
        if not filename:
            # Stock picking probably not done
            return
        file_data = BytesIO()
        w = csv.writer(file_data, delimiter=";", encoding="iso-8859-1")
        for line in self._generate_delivery_note():
            w.writerow(
                [
                    unidecode(cell) if isinstance(cell, unicode) else cell
                    for cell in line
                ]
            )
        data = file_data.getvalue()
        csv_delivery_note = self.env["ir.attachment"].search([("name", "=", filename)])
        if len(csv_delivery_note):
            csv_delivery_note[0].datas = data.encode("base_64")
        else:
            csv_delivery_note = self.env["ir.attachment"].create(
                {
                    "type": "binary",
                    "res_model": "stock.picking",
                    "res_id": self.id,
                    "name": filename,
                    "datas_fname": filename,
                    "mimetype": "text/csv",
                    "datas": data.encode("base_64"),
                }
            )

        return csv_delivery_note

    @api.multi
    def _generate_delivery_note_pdf(self):
        """Save the delivery note in pdf format in ir.attachment"""
        self.ensure_one()
        filename = self._get_delivery_note_filename(extension=".pdf")
        if not filename:
            # Stock picking probably not done
            return

        shippings = self.filtered(lambda p: p.picking_type_code == "outgoing")
        shipping_done = shippings.filtered(lambda shipping: shipping.state == "done")
        report = self.env["report"].get_pdf(
            shipping_done.ids, "stock.report_deliveryslip"
        )

        pdf_delivery_note = self.env["ir.attachment"].search([("name", "=", filename)])
        if len(pdf_delivery_note):
            pdf_delivery_note[0].datas = report.encode("base_64")
        else:
            pdf_delivery_note = self.env["ir.attachment"].create(
                {
                    "type": "binary",
                    "res_model": "stock.picking",
                    "res_id": self.id,
                    "name": filename,
                    "datas_fname": filename,
                    "mimetype": "text/pdf",
                    "datas": report.encode("base_64"),
                }
            )

        return pdf_delivery_note

    def _delivery_note_recipient_ids(self, values):
        # we could make this global for all emails by using
        # https://github.com/OCA/social/pull/329
        partner_ids = values.get("partner_ids", [])
        partners_with_emails = set()
        for partner in self.env["res.partner"].sudo().browse(partner_ids):
            current = partner
            while current:
                if current.email:
                    break
                current = current.parent_id
            partners_with_emails.add(current.id or partner.id)
        return list(partners_with_emails)

    @api.multi
    def _send_delivery_notes(self, send_csv, send_pdf):
        """Send the delivery note by email to the customer."""
        self.ensure_one()

        attachements = []
        if send_csv:
            csv_note = self._generate_delivery_note_csv()
            attachements.append(csv_note.id)

        if send_pdf:
            pdf_note = self._generate_delivery_note_pdf()
            attachements.append(pdf_note.id)

        # If no CSV or PDF is generate, no email should be sent -- case for human_drug products
        csv_filename = self._get_delivery_note_filename(extension=".csv")
        pdf_filename = self._get_delivery_note_filename(extension=".pdf")
        note_does_not_exist = not (
            self.env["ir.attachment"].search([("name", "=", csv_filename)])
            or self.env["ir.attachment"].search([("name", "=", pdf_filename)])
        )

        if note_does_not_exist:
            return

        if config["test_enable"]:
            return

        template = self.env.ref("stock_delivery_note.delivery_note_csv")
        values = template.generate_email(self.id)
        values.update(
            {
                "recipient_ids": [
                    (4, pid) for pid in self._delivery_note_recipient_ids(values)
                ],
                "auto_delete": False,
            }
        )
        if "email_from" in values and not values.get("email_from"):
            values.pop("email_from")
        values["attachment_ids"] = [(6, 0, attachements)]
        self.env["mail.mail"].create(values)

    @api.multi
    def create_delivery_note(self):
        """Used for the action menu."""
        for picking in self:
            picking._save_delivery_note()

    @api.multi
    def _generate_delivery_note(self):
        """ Generate the data for a delivery note when a stock pick is validated.

        It is a peculiar csv file because it does not have the same fields
        on each line, is structure is as folllow:

        1: Id (name of picking); email customer
        2: name customer; street customer; zip + city; country
        Next lines are the details of what is send one line by stock moves:
            Product esb_ref (default_code)
            Product name
            Product qty
            Net price without VAT
            Crude price without VAT
            Vat rate
            Lot ids
            Use dates
            Suite name

        For each line an empty column so it always ends with a semi colon
        """

        def format_number(number, fractional_size=None):
            """Format a number to a string.

            The number is formated separating the decimal and fractional part
            with a comma. With between 1 and 3 number after the comma.
            """
            if fractional_size == 1:
                formater = "{:.1f}"
            elif fractional_size == 2:
                formater = "{:.2f}"
            elif fractional_size == 3:
                formater = "{:.3f}"
            else:
                formater = "{}"
            s = formater.format(number)
            return ",".join(s.split("."))

        def get_last_column(sale_order, delivery_date):
            """ Compute last column of the delivery note.

            Don't know what it is called but it is also found on the
            deliverslip report.
            """
            customer = sale_order.partner_id
            depot_number = (
                customer.vet_depot_number or customer.parent_id.vet_depot_number
            )
            if not depot_number:
                return sale_order.client_order_ref or ""
            return "/".join(
                [
                    datetime.strptime(delivery_date, "%Y-%m-%d %H:%M:%S").strftime(
                        "%y"
                    ),
                    depot_number,
                    sale_order.suite_name or "0000",
                ]
            )

        def format_use_date(use_date):
            """Get the use dates in format dd-mm-yyyy"""
            if not use_date:
                return ""
            use_date = use_date[:10]
            return use_date[-2:] + use_date[4:8] + use_date[:4]

        self.ensure_one()
        lines = []
        partner = self.partner_id
        # The two header lines
        lines.append([self.id, partner.email or "", ""])
        lines.append(
            [
                u"{} {}".format(
                    partner.title.shortcut or "", partner.name or ""
                ).strip(),
                partner.street or "",
                u"{} {}".format(partner.zip or "", partner.city or "").strip(),
                partner.country_id.name or "",
                "",
            ]
        )

        vat_group = self.env.ref("specific_data.vat_tax_group")
        # The product lines
        grouped_lines = self.get_moves_by_order()
        for group in grouped_lines:
            for move_line in group[1][0]:
                product = move_line.product_id.with_context(lang=partner.lang)
                sol = move_line.order_line_id
                quants = move_line.get_lots(only_with_lot=False)
                quants_qty = sum([quant[1] for quant in quants])
                if quants_qty < move_line.product_qty:
                    # Sometimes get_lots does not return any quants
                    # but the quantity of the stock still as to be
                    # represtented in the delivery note
                    quants.append(["", move_line.product_qty - quants_qty, ""])
                vat = sol.tax_id.filtered(lambda r: r.tax_group_id == vat_group)
                if not vat:
                    vat = product.taxes_id.filtered(
                        lambda r: r.tax_group_id == vat_group
                    )

                for quant in quants:

                    lines.append(
                        [
                            product.default_code or "",
                            product.name,
                            # Quantity computed from the quants
                            format_number(quant[1], 3),
                            #  Net HTVA price
                            format_number(sol.price_reduce, 2)
                            if not (move_line.is_additional_move or sol.is_consignment)
                            else "",
                            #  Brut HTVA price
                            format_number(sol.price_unit, 2)
                            if not (move_line.is_additional_move or sol.is_consignment)
                            else "",
                            #  VAT rate, yes only the first one if present
                            format_number(vat[0].amount if vat else 0, 1)
                            if not (move_line.is_additional_move or sol.is_consignment)
                            else "",
                            # Lots name
                            quant[0] or "",
                            format_use_date(quant[2] or ""),
                            get_last_column(sol.order_id, self.date_done),
                            "",
                        ]
                    )
        return lines

    @api.multi
    def get_moves_by_order(self, is_entry_register=False):
        """
        Return lines for the delivery slip report.
        If the picking contains some medoc products, we have to print
        an entry register. This register will contains only medoc products.

        :param is_entry_register: Bool - if true, return only lines with
        a medoc as product.
        :return: list - list of lines
        """
        self.ensure_one()

        moves_by_order = defaultdict(list)
        backorder_moves_by_order = defaultdict(list)
        result = []
        moves_without_order = []
        backorder_moves_without_order = []

        if is_entry_register:
            lines_done = self.get_entry_register_lines()
        else:
            lines_done = self.move_lines.filtered(lambda line: line.state == "done")

        for line in lines_done:
            if not line.order_id:
                moves_without_order.append(line)
            else:
                moves_by_order[line.order_id].append(line)

        # We don't need to display backorder for the entry register
        if not is_entry_register:
            proc_groups = self.move_lines.mapped("procurement_id.group_id")
            moves = proc_groups.mapped("procurement_ids.move_ids")
            moves = moves.filtered(
                lambda rec: (
                    rec.location_dest_id.usage == "customer"
                    and rec.state not in ("cancel", "done")
                )
            )
            for line in moves:
                if not line.order_id:
                    backorder_moves_without_order.append(line)
                else:
                    backorder_moves_by_order[line.order_id].append(line)

        result_dict = {}
        for order, moves in moves_by_order.iteritems():
            result_dict[order] = [moves, backorder_moves_by_order.get(order, [])]
        if moves_without_order:
            result.append((None, (moves_without_order, backorder_moves_without_order)))

        result.extend(
            sorted(
                result_dict.items(),
                key=lambda picking: (picking[0][0].date_order, picking[0][0].id),
            )
        )
        return result

    def get_entry_register_lines(self):
        categ_vet = self.env.ref("specific_data.product_categ_vet_belges")
        categ_import = self.env.ref("specific_data.product_categ_importation")

        all_products = self.mapped("move_lines.product_id")
        medic_products = self.env["product.product"].search(
            [
                "|",
                ("categ_id", "child_of", categ_vet.id),
                ("categ_id", "child_of", categ_import.id),
                ("id", "in", all_products.ids),
            ],
            order="categ_id",
        )

        lines = self.mapped("move_lines").filtered(
            lambda line: line.state == "done" and line.product_id in medic_products
        )

        return lines
