# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    additional_product_id = fields.Many2one('product.template',
                                            string='Additional product')
    ratio_main_product = fields.Integer('Ratio main product')
    ratio_additional_product = fields.Integer('Ration additional product')

    @api.multi
    def get_qty_additional_product(self, ordered_qty):
        self.ensure_one()

        if not self.additional_product_id \
                or not self.ratio_main_product \
                or not self.ratio_additional_product:
            return 0

        coefficient = self.ratio_main_product / ordered_qty
        qty_additional_product = coefficient * self.ratio_additional_product

        return qty_additional_product
