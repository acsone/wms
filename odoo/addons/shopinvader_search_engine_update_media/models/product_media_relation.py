# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class ProductMediaRelation(models.Model):
    _name = "product.media.relation"
    _inherit = ["product.media.relation", "product.update.mixin"]

    def get_products(self):
        return self.mapped("product_tmpl_id")
