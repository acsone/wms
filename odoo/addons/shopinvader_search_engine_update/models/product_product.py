# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def write(self, vals):
        # maybe do something more clever?
        res = super(ProductProduct, self).write(vals)
        self.shopinvader_mark_to_update()
        return res

    def shopinvader_mark_to_update(self):
        if self.mapped("shopinvader_bind_ids"):
            self.mapped("shopinvader_bind_ids").write({"to_update": "true"})
