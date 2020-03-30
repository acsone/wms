# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('tax_id')
    def _check_only_one_vat(self):
        vat_group = self.env.ref('specific_data.vat_tax_group')
        vat_taxes = self.tax_id.filtered(lambda r: r.tax_group_id == vat_group)
        if len(vat_taxes) > 1:
            raise ValidationError(
                _(
                    'For %s multiple tax from the VAT group are selected. Only one is allowed.'
                )
                % (self.product_id.display_name,)
            )

    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        """Warning if multiple VAT taxes are selected."""
        try:
            self._check_only_one_vat()
        except ValidationError:
            warning_mess = {
                'title': _('More than one VAT tax selected!'),
                'message': _(
                    'You selected more than one tax of type VAT on a sale '
                    'order line, it does not make sense.'
                ),
            }
            return {'warning': warning_mess}
        return {}
