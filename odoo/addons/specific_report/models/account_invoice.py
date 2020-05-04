# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import config


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice", "report.async"]

    amount_without_discount = fields.Monetary(compute="_compute_total_amounts")

    amount_supplier_discount = fields.Monetary(compute="_compute_total_amounts")

    amount_alcyon_discount = fields.Monetary(compute="_compute_total_amounts")

    amount_discount_total = fields.Monetary(compute="_compute_total_amounts")

    amount_untaxed_with_contribution = fields.Monetary(compute="_compute_total_amounts")

    invoice_apb_ids = fields.Many2many(
        "account.invoice.tax", compute="_compute_total_amounts"
    )
    amount_apb = fields.Monetary(compute="_compute_total_amounts")

    invoice_antibiotics_ids = fields.Many2many(
        "account.invoice.tax", compute="_compute_total_amounts"
    )
    amount_antibiotics = fields.Monetary(compute="_compute_total_amounts")

    invoice_contribution_ids = fields.Many2many(
        "account.invoice.tax", compute="_compute_total_amounts"
    )
    amount_contribution = fields.Monetary(compute="_compute_total_amounts")

    invoice_only_tax_ids = fields.Many2many(
        "account.invoice.tax", compute="_compute_total_amounts"
    )
    amount_only_tax = fields.Monetary(compute="_compute_total_amounts")

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.quantity",
        "invoice_line_ids.price_unit",
        "invoice_line_ids.discount2",
        "invoice_line_ids.discount3",
        "invoice_line_ids.amount_discount2",
        "invoice_line_ids.amount_discount3",
        "tax_line_ids",
    )
    def _compute_total_amounts(self):
        tax_group_apb = self.env.ref("specific_account.tax_group_apb")
        tax_group_antibiotics = self.env.ref("account.tax_group_taxes")
        for inv in self:
            inv.amount_supplier_discount = sum(
                [l.amount_discount2 for l in inv.invoice_line_ids]
            )
            inv.amount_alcyon_discount = sum(
                [l.amount_discount3 for l in inv.invoice_line_ids]
            )

            inv.amount_discount_total = (
                inv.amount_supplier_discount + inv.amount_alcyon_discount
            )

            amount_apb = amount_antibiotics = amount_contribution = amount_only_tax = 0
            invoice_only_tax_ids = self.env["account.invoice.tax"]
            invoice_contribution_ids = self.env["account.invoice.tax"]
            invoice_apb_ids = self.env["account.invoice.tax"]
            invoice_antibiotics_ids = self.env["account.invoice.tax"]

            for invoice_tax in inv.tax_line_ids:
                if invoice_tax.tax_id.include_base_amount:
                    invoice_contribution_ids |= invoice_tax
                    amount_contribution += invoice_tax.amount
                elif invoice_tax.tax_id.tax_group_id == tax_group_apb:
                    invoice_apb_ids |= invoice_tax
                    amount_apb += invoice_tax.amount
                elif invoice_tax.tax_id.tax_group_id == tax_group_antibiotics:
                    invoice_antibiotics_ids |= invoice_tax
                    amount_antibiotics += invoice_tax.amount
                else:
                    invoice_only_tax_ids |= invoice_tax
                    amount_only_tax += invoice_tax.amount
            inv.amount_apb = amount_apb
            inv.amount_antibiotics = amount_antibiotics
            inv.amount_contribution = amount_contribution
            inv.amount_only_tax = amount_only_tax
            inv.invoice_only_tax_ids = invoice_only_tax_ids
            inv.invoice_contribution_ids = invoice_contribution_ids
            inv.invoice_apb_ids = invoice_apb_ids
            inv.invoice_antibiotics_ids = invoice_antibiotics_ids

            inv.amount_without_discount = (
                sum([l.price_unit * l.quantity for l in inv.invoice_line_ids])
                + amount_contribution
            )

            inv.amount_untaxed_with_contribution = (
                inv.amount_untaxed + amount_contribution
            )

    @api.multi
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

    @api.multi
    def get_instrastat_values(self):
        values_by_intrastat = {}

        for line in self.invoice_line_ids:
            if not line.product_id or not line.product_id.intrastat_id:
                continue
            intrastat = line.product_id.intrastat_id

            weight = line.product_id.weight * line.quantity
            amount = line.price_subtotal

            intrastat_value = values_by_intrastat.get(intrastat.name, [])
            if not intrastat_value:
                intrastat_value = [weight, amount]
            else:
                total_weight = intrastat_value[0] + weight
                total_amount = intrastat_value[1] + amount
                intrastat_value = [total_weight, total_amount]

            values_by_intrastat[intrastat.name] = intrastat_value

        values = [
            (code, value[0], value[1])
            for code, value in values_by_intrastat.iteritems()
        ]
        values.sort(key=lambda line: line[0])

        return values

    @api.multi
    def get_report_name(self):
        """Generate a specific name for the report save in ir.attachment.

        If no name is returned, the file is not saved.
        """
        self.ensure_one()
        if self.type in ["in_invoice", "in_refund"] or self.state == "draft":
            # Only generate for client invoice and credit notes
            # And not for invoice in draft state
            return None
        type_doc = ""
        if self.type == "out_invoice":
            type_doc = "fc"
        elif self.type == "out_refund":
            type_doc = "nc"
        return (
            "_".join(
                [
                    type_doc,
                    self.partner_id.ref or "",
                    str(self.id),
                    "".join(self.create_date[:10].split("-")),
                    "".join(self.create_date[-8:].split(":")),
                ]
            )
            + ".pdf"
        )

    @api.multi
    def action_invoice_open(self):
        """Generate the invoice pdf and save it to ir.attachment """
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            if invoice.type not in ("out_invoice", "out_refund"):
                continue
            invoice.with_delay(priority=4).print_and_attach_report(
                "account.report_invoice"
            )
        return res

    @api.multi
    def invoice_print(self):
        """Only keep one invoice with the same name"""
        self.ensure_one()
        res = super(AccountInvoice, self).invoice_print()
        if config["test_enable"]:
            # Do not generate the report during test
            return res
        filename = self.get_report_name()
        existing = self.env["ir.attachment"].search(
            [("name", "=", filename), ("res_model", "=", "account.invoice")]
        )
        existing.unlink()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    only_tax_ids = fields.Many2many("account.tax", compute="_compute_all_taxes")
    contribution_ids = fields.Many2many("account.tax", compute="_compute_all_taxes")
    apb_ids = fields.Many2many("account.tax", compute="_compute_all_taxes")
    amount_contribution = fields.Monetary(compute="_compute_all_taxes")

    amount_discount2 = fields.Monetary(compute="_compute_price_discount_amount")

    amount_discount3 = fields.Monetary(compute="_compute_price_discount_amount")

    @api.multi
    @api.depends(
        "price_unit", "price_subtotal", "discount", "discount2", "discount3", "quantity"
    )
    def _compute_price_discount_amount(self):
        """ We need to compute discount line by line to prevent
        rounding issue if compute globally"""
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

    @api.multi
    @api.depends("invoice_line_tax_ids")
    def _compute_all_taxes(self):
        tax_group_apb = self.env.ref("specific_account.tax_group_apb")

        for line in self:
            amount_contribution = 0
            only_tax_ids = self.env["account.tax"]
            contribution_ids = self.env["account.tax"]
            apb_ids = self.env["account.tax"]

            for tax in line.invoice_line_tax_ids:
                if tax.include_base_amount:
                    amount_contribution += tax.amount * line.quantity
                    contribution_ids |= tax
                elif tax.tax_group_id == tax_group_apb:
                    apb_ids |= tax
                else:
                    only_tax_ids |= tax

            line.only_tax_ids = only_tax_ids
            line.contribution_ids = contribution_ids
            line.apb_ids = apb_ids
            line.amount_contribution = amount_contribution
