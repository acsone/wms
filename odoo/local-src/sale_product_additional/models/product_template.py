# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    additional_product_ids = fields.One2many(
        comodel_name='product.template.additional',
        inverse_name='original_product_id',
        string='Additional products',
        copy=False
    )

    @api.one
    @api.constrains('additional_product_ids')
    def _check_additional_product_ids(self):
        """
            We check if
            a product don't have 2 additional products with the same product.
            Because with this case,
            we can't compute correctly the additional lines on sale order.
        """
        current_products = []
        for additional_product in self.additional_product_ids:
            if additional_product.product_id in current_products:
                raise ValidationError(
                    "Additional products have duplicates")
            current_products.append(additional_product.product_id)
