# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange("invoice_line_tax_ids")
    def _onchange_invoice_line_tax_ids(self):
        """Warning if multiple VAT taxes are selected."""
        vat_group = self.env.ref("specific_data.vat_tax_group")
        vat_taxes = self.invoice_line_tax_ids.filtered(
            lambda r: r.tax_group_id == vat_group
        )
        if len(vat_taxes) > 1:
            warning_mess = {
                "title": _("More than one VAT tax selected!"),
                "message": _(
                    "You selected more than one tax of type VAT on an invoice line, it does not make sense."
                ),
            }
            return {"warning": warning_mess}
        return {}
