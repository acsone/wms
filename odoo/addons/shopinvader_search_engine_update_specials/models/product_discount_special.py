# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class ProductDiscountSpecial(models.Model):
    _inherit = "product.discount.special"

    @api.model
    def create(self, values):
        res = super(ProductDiscountSpecial, self).create(values)
        res.product_template_id.shopinvader_mark_to_update()
        return res

    def write(self, vals):
        res = super(ProductDiscountSpecial, self).write(vals)
        self.mapped("product_template_id").shopinvader_mark_to_update()
        return res

    def unlink(self):
        products = self.mapped("product_template_id")
        res = super(ProductDiscountSpecial, self).unlink()
        products.shopinvader_mark_to_update()
        return res
