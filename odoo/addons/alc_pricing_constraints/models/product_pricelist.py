# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model
    def create(self, vals):
        # prevent the addition of a useless item that would violate a constraint
        if "item_ids" not in vals:
            vals["item_ids"] = [(6, 0, [])]
        else:  # the interface already gave a useless items to arguments...
            vals["item_ids"] = [
                item
                for item in vals["item_ids"]
                if item[0] != 0  # in a create, one2many create command
                or not self.env["product.pricelist.item"]._is_useless_vals(item[2])
            ]
        return super(ProductPricelist, self).create(vals)
