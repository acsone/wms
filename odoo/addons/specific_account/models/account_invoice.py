# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        """ Fix puchase module that override journal based on currency.
        On the screen, the journal is first selected, then the supplier
        and it's not expected to have the journal changed back automatically
        """
        journal = self.journal_id
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.journal_id != journal:
            self.journal_id = journal
        return res

    @api.onchange("partner_id")
    def _onchange_intrastat_country(self):
        self.intrastat_country_id = self.partner_id.country_id

    def _prepare_invoice_line_from_po_line(self, line):
        """Overloaded to snapshot the qty received and the ordered qty from
        the purchase order line when the invoice line is created.
        """
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        data["purchase_line_qty_received"] = line.qty_received
        data["purchase_line_product_qty"] = line.product_qty
        return data


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    invoice_state = fields.Selection(related="invoice_id.state", readonly=True)
    purchase_line_qty_received = fields.Float(string="Received Qty", readonly=True)
    purchase_line_product_qty = fields.Float(string="Ordered Qty", readonly=True)

    @api.multi
    def unlink(self):
        """Force tax compuation when a line is deleted."""
        invoices = self.mapped("invoice_id")
        res = super(AccountInvoiceLine, self).unlink()
        if self.env.context.get("recompute_taxes_on_delete"):
            invoices.compute_taxes()
        return res

    @api.model
    @api.returns("self", lambda value: value.id)
    def create(self, values):
        rec = super(AccountInvoiceLine, self).create(values)
        if self.env.context.get("recompute_taxes_on_delete"):
            # we remove the recompute_taxes_on_delete context key becase the
            # triple discount module will trigger a write on the invoice lines
            # when we call invoice.compute_taxes and we want to avoid a
            # recursive call to write in that case
            invoice = rec.invoice_id.with_context(recompute_taxes_on_delete=False)
            invoice.compute_taxes()
        return rec

    @api.multi
    def write(self, values):
        res = super(AccountInvoiceLine, self).write(values)
        if self.env.context.get("recompute_taxes_on_delete"):
            # we remove the recompute_taxes_on_delete context key becase the
            # triple discount module will trigger a write on the invoice lines
            # when we call invoice.compute_taxes and we want to avoid a
            # recursive call to write in that case
            invoices = self.mapped("invoice_id").with_context(
                recompute_taxes_on_delete=False
            )
            invoices.compute_taxes()
        return res
