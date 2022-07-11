# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _cache_discount(self, product):
        res = super(ProductPricelistItem, self)._cache_discount(product)
        if res:
            res["exclusive"] = self.exclusive
        return res
