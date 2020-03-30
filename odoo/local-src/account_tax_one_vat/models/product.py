# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('taxes_id')
    def _check_only_one_vat_customer_tax(self):
        vat_group = self.env.ref('specific_data.vat_tax_group')
        vat_taxes = self.taxes_id.filtered(
            lambda r: r.tax_group_id == vat_group
        )
        if len(vat_taxes) > 1:
            raise ValidationError(
                _(
                    'Multiple customer tax of type VAT are selected. Only one is allowed.'
                )
            )

    @api.constrains('supplier_taxes_id')
    def _check_only_one_vat_supplier_tax(self):
        vat_group = self.env.ref('specific_data.vat_tax_group')
        vat_taxes = self.supplier_taxes_id.filtered(
            lambda r: r.tax_group_id == vat_group
        )
        if len(vat_taxes) > 1:
            raise ValidationError(
                _(
                    'Multiple supplier tax of type VAT are selected. Only one is allowed.'
                )
            )
