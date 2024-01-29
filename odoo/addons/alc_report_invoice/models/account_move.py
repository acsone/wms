# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from odoo import api, fields
from odoo.tools import config

from odoo.addons.account.models.account_move import AccountMove as Move
from odoo.addons.account.models.account_move_line import AccountMoveLine as MoveLine
from odoo.addons.account.models.account_tax import AccountTax
from odoo.addons.alc_report_base.models.report_async import ReportAsync


class AccountMove(Move, ReportAsync):
    _name = "account.move"

    amount_supplier_discount = fields.Monetary(compute="_compute_total_amounts")
    amount_alcyon_discount = fields.Monetary(compute="_compute_total_amounts")
    amount_discount_total = fields.Monetary(compute="_compute_total_amounts")
    amount_untaxed_with_contribution = fields.Monetary(compute="_compute_total_amounts")
    invoice_apb_ids = fields.Many2many[AccountTax](compute="_compute_total_amounts")
    invoice_antibiotics_ids = fields.Many2many[AccountTax](
        compute="_compute_total_amounts"
    )
    invoice_contribution_ids = fields.Many2many[AccountTax](
        compute="_compute_total_amounts"
    )
    invoice_only_tax_ids = fields.Many2many[AccountTax](
        compute="_compute_total_amounts"
    )
    payment_mode_description = fields.Char(
        compute="_compute_payment_mode_description_on_invoice"
    )

    def _compute_payment_mode_description_on_invoice(self):
        for move in self:
            payment_mode = self.env["account.payment.mode"].search(
                [("id", "=", move.payment_mode_id.id)]
            )
            move.payment_mode_description = (
                payment_mode.invoice_description
                if payment_mode.invoice_description
                else ""
            )

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.quantity",
        "invoice_line_ids.price_unit",
        "invoice_line_ids.discount2",
        "invoice_line_ids.discount3",
        "invoice_line_ids.amount_discount2",
        "invoice_line_ids.amount_discount3",
        "invoice_line_ids.tax_ids",
    )
    def _compute_total_amounts(self):
        tax_group_apb = self.env.ref("alc_accounting_data.tax_group_apb")
        tax_group_antibiotics = self.env.ref("account.tax_group_taxes")
        for move in self:
            move.amount_supplier_discount = sum(
                line.amount_discount2 for line in move.invoice_line_ids
            )
            move.amount_alcyon_discount = sum(
                line.amount_discount3 for line in move.invoice_line_ids
            )

            move.amount_discount_total = (
                move.amount_supplier_discount + move.amount_alcyon_discount
            )

            invoice_only_tax_ids = self.env["account.tax"]
            invoice_contribution_ids = self.env["account.tax"]
            invoice_apb_ids = self.env["account.tax"]
            invoice_antibiotics_ids = self.env["account.tax"]

            for tax in move.invoice_line_ids.tax_ids:
                if tax.include_base_amount:
                    invoice_contribution_ids |= tax
                elif tax.tax_group_id == tax_group_apb:
                    invoice_apb_ids |= tax
                elif tax.tax_group_id == tax_group_antibiotics:
                    invoice_antibiotics_ids |= tax
                else:
                    invoice_only_tax_ids |= tax
            move.invoice_only_tax_ids = invoice_only_tax_ids
            move.invoice_contribution_ids = invoice_contribution_ids
            move.invoice_apb_ids = invoice_apb_ids
            move.invoice_antibiotics_ids = invoice_antibiotics_ids

    def get_lines_by_sale(self):
        self.ensure_one()

        result = []
        sales = defaultdict(list)
        orphans = []
        for line in self.invoice_line_ids:
            order = line.sale_line_ids.mapped("order_id")
            if not order:
                orphans.append(line)

            elif len(order) > 1:
                raise ValueError("Multiple sale order for one invoice line.")

            else:
                sales[order].append(line)

        if orphans:
            result.append((None, orphans))

        result.extend(sorted(sales.items(), key=lambda x: (x[0].date_order, x[0].id)))
        return result

    def get_instrastat_values(self):
        values_by_intrastat = {}

        for line in self.invoice_line_ids:
            if not line.product_id or not line.product_id.has_intrastat:
                continue
            intrastat_name = line.product_id.intrastat_code_name

            weight = line.product_id.weight * line.quantity
            amount = line.price_subtotal

            intrastat_value = values_by_intrastat.get(intrastat_name, [])
            if not intrastat_value:
                intrastat_value = [weight, amount]
            else:
                total_weight = intrastat_value[0] + weight
                total_amount = intrastat_value[1] + amount
                intrastat_value = [total_weight, round(total_amount, 2)]

            values_by_intrastat[intrastat_name] = intrastat_value

        values = [
            (code, value[0], value[1]) for code, value in values_by_intrastat.items()
        ]
        values.sort(key=lambda line: line[0])

        return values

    def get_report_name(self):
        """Generate a specific name for the report save in ir.attachment.

        If no name is returned, the file is not saved.
        """
        self.ensure_one()
        if self.move_type in ["in_invoice", "in_refund"] or self.state == "draft":
            # Only generate for client invoice and credit notes
            # And not for invoice in draft state
            return None
        type_doc = ""
        if self.move_type == "out_invoice":
            type_doc = "fc"
        elif self.move_type == "out_refund":
            type_doc = "nc"
        return (
            "_".join(
                [
                    type_doc,
                    self.partner_id.ref or "",
                    str(self.id),
                    self.create_date.strftime("%Y%m%d"),
                    self.create_date.strftime("%H%M%S"),
                ]
            )
            + ".pdf"
        )

    def action_post(self):
        """Generate the invoice pdf and save it to ir.attachment."""
        res = super().action_post()
        for move in self:
            if move.move_type not in ("out_invoice", "out_refund"):
                continue
            move.with_delay(priority=4).print_and_attach_report(
                "account.report_invoice"
            )
        return res

    def action_invoice_print(self):
        """Only keep one invoice with the same name."""
        self.ensure_one()
        res = super().action_invoice_print()
        if config["test_enable"]:
            # Do not generate the report during test
            return res
        filename = self.get_report_name()
        existing = self.env["ir.attachment"].search(
            [("name", "=", filename), ("res_model", "=", "account.invoice")]
        )
        existing.unlink()
        return res

    def _get_taxes_summary(self):
        """
        Compute and format taxes and amounts infos needed for reporting.

        :return: dict {'tax_type': list,...,
                       'amount_without_discount': float,
                       'amount_untaxed_with_contribution': float,}
        """
        self.ensure_one()
        # get all taxes from each invoice line
        all_taxes = []
        for line in self.invoice_line_ids:
            taxes = self.env["account.tax"]._compute_taxes_for_single_line(
                line._convert_to_tax_base_line_dict()
            )
            if taxes:
                all_taxes += taxes[1]
        # summarize taxes for each tax type
        tax_types = {
            "invoice": self.invoice_only_tax_ids,
            "apb": self.invoice_apb_ids,
            "antibiotics": self.invoice_antibiotics_ids,
        }
        tax_summary = {}
        for name, tax_ids in tax_types.items():
            tax_summary[name] = []
            tax_total = 0
            for tax in tax_ids:
                taxes = [t for t in all_taxes if t["id"] == tax.id]
                tax_amount = sum(t["tax_amount"] for t in taxes)
                tax_summary[name].append(
                    {
                        "rate": f"{tax.amount:.2f}",
                        "base_amount": f"{sum(t['base_amount'] for t in taxes):.2f} "
                        f"{self.currency_id.symbol}",
                        "tax_amount": f"{tax_amount:.2f} {self.currency_id.symbol}",
                    }
                )
                tax_total += tax_amount
            tax_summary[f"{name}_total_tax_amount"] = (
                f"{tax_total:.2f} " f"{self.currency_id.symbol}"
            )
            tax_summary[f"{name}_total"] = tax_total  # needed for amounts below
        # The job is already done in lines for contribution_ids
        tax_summary["contribution_total"] = sum(
            line.amount_contribution for line in self.invoice_line_ids
        )
        tax_summary[
            "contribution_total_tax_amount"
        ] = f"{tax_summary['contribution_total']:.2f} {self.currency_id.symbol}"
        # add some computed amounts needed for reporting
        amount_without_discount = (
            sum(
                line.price_unit * line.quantity
                for line in self.invoice_line_ids
                if line.display_type == "product"
            )
            + tax_summary["contribution_total"]
        )
        tax_summary["amount_without_discount"] = (
            f"{amount_without_discount:.2f} " f"{self.currency_id.symbol}"
        )
        amount_untaxed_with_contribution = (
            self.amount_untaxed + tax_summary["contribution_total"]
        )
        tax_summary[
            "amount_untaxed_with_contribution"
        ] = f"{amount_untaxed_with_contribution:.2f} {self.currency_id.symbol}"
        return tax_summary


class AccountMoveLine(MoveLine):

    only_tax_ids = fields.Many2many[AccountTax](compute="_compute_all_taxes")
    contribution_ids = fields.Many2many[AccountTax](compute="_compute_all_taxes")
    apb_ids = fields.Many2many[AccountTax](compute="_compute_all_taxes")
    amount_contribution = fields.Monetary(compute="_compute_all_taxes")

    amount_discount2 = fields.Monetary(compute="_compute_price_discount_amount")

    amount_discount3 = fields.Monetary(compute="_compute_price_discount_amount")

    @api.depends(
        "price_unit", "price_subtotal", "discount", "discount2", "discount3", "quantity"
    )
    def _compute_price_discount_amount(self):
        """We need to compute discount line by line to prevent.

        rounding issue if compute globally
        """
        for line in self:
            if line.discount2 and not line.discount3:
                line.amount_discount2 = (
                    line.quantity * line.price_unit
                ) - line.price_subtotal
                line.amount_discount3 = 0.0
            elif not line.discount2 and line.discount3:
                line.amount_discount3 = (
                    line.quantity * line.price_unit
                ) - line.price_subtotal
                line.amount_discount2 = 0.0
            elif line.discount3 and line.discount2:
                line.amount_discount2 = (
                    line.quantity * line.price_unit * ((line.discount2 or 0.0) / 100.0)
                )
                line.amount_discount3 = (
                    (line.quantity * line.price_unit)
                    - line.price_subtotal
                    - line.amount_discount2
                )
            else:
                line.amount_discount3 = 0.0
                line.amount_discount2 = 0.0

    @api.depends("tax_ids")
    def _compute_all_taxes(self):
        tax_group_apb = self.env.ref("alc_accounting_data.tax_group_apb")
        for line in self:
            amount_contribution = 0
            only_tax_ids = self.env["account.tax"]
            contribution_ids = self.env["account.tax"]
            apb_ids = self.env["account.tax"]
            for tax in line.tax_ids:
                if tax.include_base_amount:
                    taxes = self.env["account.tax"]._compute_taxes_for_single_line(
                        line._convert_to_tax_base_line_dict()
                    )[1]
                    mytax = [t for t in taxes if t["id"] == tax.id][0]
                    amount_contribution += mytax["tax_amount"]
                    contribution_ids |= tax
                elif tax.tax_group_id == tax_group_apb:
                    apb_ids |= tax
                else:
                    only_tax_ids |= tax
            line.only_tax_ids = only_tax_ids
            line.contribution_ids = contribution_ids
            line.apb_ids = apb_ids
            line.amount_contribution = amount_contribution
