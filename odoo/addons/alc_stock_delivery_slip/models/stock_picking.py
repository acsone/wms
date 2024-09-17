# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
from collections import defaultdict
from io import BytesIO

import unicodecsv as csv
from unidecode import unidecode

from odoo.fields import Command
from odoo.tools import config

from odoo.addons.delivery.models import stock_picking


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


def format_use_date(use_date):
    """Get the use dates in format dd-mm-yyyy."""
    if not use_date:
        return ""
    sz_use_date = use_date.isoformat()[:10]
    return sz_use_date[-2:] + sz_use_date[4:8] + sz_use_date[:4]


class StockPicking(stock_picking.StockPicking):
    def _action_done(self):
        to_do = self.filtered(lambda p: p.state not in ("cancel", "done"))
        result = super()._action_done()
        picking_type_out = self.env.ref("stock.picking_type_out")
        if self.env.context.get("skip_pdf_gen"):
            return result
        for r in to_do:
            if (
                r.picking_type_id == picking_type_out
                and r.date_done
                and r.state == "done"
            ):
                r._send_delivery_notes(
                    r.customer_id.send_csv_deliveryship,
                    r.customer_id.send_pdf_deliveryship,
                )
        return result

    def _get_delivery_note_filename(self, extension):
        """Return the delivery note filename."""
        self.ensure_one()
        if not self.date_done:
            return None
        sale_orders = self.move_ids.mapped("order_id")
        sz_date_done = self.date_done.strftime("%Y-%m-%d %H:%M:%S")
        picking_number = self.name.split("/")[-1]
        return (
            "_".join(
                [
                    "NE",
                    sale_orders[0].partner_id.ref or "" if len(sale_orders) > 0 else "",
                    picking_number,
                    "".join(sz_date_done[:10].split("-")),
                    "".join(sz_date_done[-8:].split(":")),
                ]
            )
            + extension
        )

    def _generate_delivery_note_csv(self):
        """Save the delivery note in csv format in ir.attachment."""
        self.ensure_one()
        filename = self._get_delivery_note_filename(extension=".csv")
        if not filename:
            # Stock picking probably not done
            return None
        file_data = BytesIO()
        w = csv.writer(file_data, delimiter=";", encoding="iso-8859-1")
        for line in self._generate_delivery_note():
            w.writerow(
                [unidecode(cell) if isinstance(cell, str) else cell for cell in line]
            )
        data = file_data.getvalue()
        csv_delivery_note = self.env["ir.attachment"].search([("name", "=", filename)])
        if len(csv_delivery_note) > 0:
            csv_delivery_note[0].datas = data.encode("base_64")
        else:
            csv_delivery_note = self.env["ir.attachment"].create(
                {
                    "type": "binary",
                    "res_model": "stock.picking",
                    "res_id": self.id,
                    "name": filename,
                    "mimetype": "text/csv",
                    "datas": base64.encodebytes(data),
                }
            )

        return csv_delivery_note

    def _generate_delivery_note_pdf(self):
        """Save the delivery note in pdf format in ir.attachment."""
        self.ensure_one()
        filename = self._get_delivery_note_filename(extension=".pdf")
        if not filename:
            # Stock picking probably not done
            return None

        shippings = self.filtered(lambda p: p.picking_type_code == "outgoing")
        shipping_done = shippings.filtered(lambda shipping: shipping.state == "done")
        action_report = self.env.ref("stock.action_report_delivery")
        pdf_report = action_report._render_qweb_pdf(
            "stock.report_deliveryslip", shipping_done.ids
        )[0]

        pdf_delivery_note = self.env["ir.attachment"].search([("name", "=", filename)])
        if len(pdf_delivery_note) > 0:
            pdf_delivery_note[0].datas = base64.encodebytes(pdf_report)
        else:
            pdf_delivery_note = self.env["ir.attachment"].create(
                {
                    "type": "binary",
                    "res_model": "stock.picking",
                    "res_id": self.id,
                    "name": filename,
                    "mimetype": "text/pdf",
                    "datas": base64.encodebytes(pdf_report),
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

        # If no CSV or PDF has been generated, no email should be sent -- case for
        # human_drug products
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

        template = self.env.ref("alc_stock_delivery_slip.delivery_note_csv")
        values = template.generate_email(
            self.id,
            [
                "subject",
                "body_html",
                "email_from",
                "email_to",
                "email_cc",
                "reply_to",
                "partner_to",
            ],
        )
        values.update(
            {
                "recipient_ids": [
                    Command.link(pid)
                    for pid in self._delivery_note_recipient_ids(values)
                ],
                "auto_delete": False,
            }
        )
        if "email_from" in values and not values.get("email_from"):
            values.pop("email_from")
        values["attachment_ids"] = [Command.set(attachements)]
        self.env["mail.mail"].sudo().create(values)

    def create_delivery_note(self):
        """Used for the action menu."""
        for picking in self:
            picking._generate_delivery_note_csv()

    def _generate_delivery_note(self):
        """Generate the data for a delivery note when a stock pick is validated.

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
            Product AMM if exist
            Delivery date

        For each line an empty column so it always ends with a semi colon
        """

        self.ensure_one()
        lines = []
        partner = self.partner_id
        # The two header lines
        picking_number = self.name.split("/")[-1]
        lines.append([picking_number, partner.email or "", ""])
        lines.append(
            [
                f"{partner.title.shortcut or ''} {partner.name or ''}".strip(),
                partner.street or "",
                f"{partner.zip or ''} {partner.city or ''}".strip(),
                partner.country_id.name or "",
                "",
            ]
        )

        # The product lines
        grouped_lines = self.get_moves_by_order()
        for group in grouped_lines:
            for move_line in group[1][0]:
                product = move_line.product_id.with_context(lang=partner.lang)
                sol = move_line.sale_line_id
                stock_move_lines = move_line.get_lots()
                smlines_qty = sum(smline[1] for smline in stock_move_lines)
                if smlines_qty < move_line.product_qty:
                    # Sometimes get_lots does not return any quants
                    # but the quantity of the stock still has to be
                    # represtented in the delivery note
                    stock_move_lines.append(
                        ["", move_line.product_qty - smlines_qty, ""]
                    )
                vat = sol.tax_id.filtered(lambda r: r.is_vat)
                if not vat:
                    vat = product.taxes_id.filtered(lambda r: r.is_vat)

                for smline in stock_move_lines:

                    lines.append(
                        [
                            product.default_code or "",
                            product.name,
                            # Quantity computed from the quants
                            format_number(smline[1], 3),
                            #  Net HTVA price
                            format_number(move_line._get_net_price(), 2),
                            #  Brut HTVA price
                            format_number(move_line._get_crude_price(), 2),
                            #  VAT rate, yes only the first one if present
                            format_number(vat[0].amount if vat else 0, 1),
                            # Lots name
                            smline[0] or "",
                            format_use_date(smline[2] or ""),
                            move_line._get_suite_name(sol.order_id, self.date_done),
                            # Product AMM if exist and delivery date
                            format_use_date(self.date_done or ""),
                            product.code_amm or "",
                            "",
                        ]
                    )
        return lines

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
        elif self.picking_type_code == "incoming":
            lines_done = self.move_ids
        else:
            lines_done = self.move_ids.filtered(lambda line: line.state == "done")

        for line in lines_done:
            if not line.order_id:
                moves_without_order.append(line)
            else:
                moves_by_order[line.order_id].append(line)

        # We don't need to display backorder for the entry register
        if not is_entry_register:
            backorders = self.backorder_ids.filtered(
                lambda rec: rec.state not in ("cancel", "done")
            )
            proc_groups = self.move_ids.mapped("group_id") | backorders.mapped(
                "group_id"
            )
            moves = proc_groups.mapped("stock_move_ids")
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
        for order, moves in moves_by_order.items():
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
        categ_vet = self.env.ref("alc_product_category_data.product_categ_vet_belges")
        categ_import = self.env.ref(
            "alc_product_category_data.product_categ_importation"
        )

        all_products = self.mapped("move_ids.product_id")

        lines = self.mapped("move_ids").filtered(
            lambda line: line.product_id.id in all_products.ids
            and (
                line.product_id.categ_id.has_for_parent(categ_vet)
                or line.product_id.categ_id.has_for_parent(categ_import)
            )
        )
        if self.picking_type_code != "incoming":
            lines = lines.filtered(lambda line: line.state == "done")
        return lines
