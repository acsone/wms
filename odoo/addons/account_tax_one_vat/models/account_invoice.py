# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _name = "account.invoice.line"
    _inherit = ["account.invoice.line", "one.vat.mixin"]

    @api.onchange("invoice_line_tax_ids")
    def _onchange_invoice_line_tax_ids(self):
        return self._onchange_one_vat_tax_field("invoice_line_tax_ids")
