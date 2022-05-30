# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ProductDiscountSpecial(models.Model):
    _name = "product.discount.special"
    _inherit = ["product.discount.special", "product.update.mixin"]

    def get_products(self):
        return self.mapped("product_template_id")
