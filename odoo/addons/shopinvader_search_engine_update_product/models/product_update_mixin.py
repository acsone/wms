# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class ProductUpdateMixin(models.AbstractModel):
    _name = "product.update.mixin"

    @api.model
    def create(self, values):
        res = super(ProductUpdateMixin, self).create(values)
        res.get_products().shopinvader_mark_to_update()
        return res

    def write(self, vals):
        needs_update = self.needs_product_update(vals)
        if needs_update:
            products = self.get_products()
        res = super(ProductUpdateMixin, self).write(vals)
        if needs_update:
            (products | self.get_products()).shopinvader_mark_to_update()
        return res

    def unlink(self):
        products = self.get_products()
        res = super(ProductUpdateMixin, self).unlink()
        products.shopinvader_mark_to_update()
        return res

    def get_products(self):
        raise NotImplementedError

    def needs_product_update(self, vals):
        return True
