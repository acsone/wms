# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        """Warning if multiple VAT taxes are selected."""
        vat_group = self.env.ref('stock_delivery_note.vat_tax_group')
        vat_taxes = self.tax_id.filtered(lambda r: r.tax_group_id == vat_group)
        if len(vat_taxes) > 1:
            warning_mess = {
                'title': _('More than one VAT tax selected!'),
                'message': _(
                    'You selected more than one tax of type VAT on an sale '
                    'order line, it does not make sense.'
                ),
            }
            return {'warning': warning_mess}
        return {}
