# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


def is_useless_item_vals(item_vals):
    useless = False
    compute_price = item_vals.get("compute_price", "fixed")
    if compute_price == "percentage":
        useless = item_vals.get("percent_price", 0) == 0
    elif compute_price == "formula":
        no_surcharge = item_vals.get("price_surcharge", 0) == 0
        useless = no_surcharge and item_vals.get("price_discount", 0) == 0
    return useless


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model
    def create(self, vals):
        # slight optimisation: prevent the addition of a useless global item
        # note that 'useless items' might be useful (by preventing discounts from
        # applying on a certain product) but if we are provided with only useless items
        # we assume it was given by the interface
        if "item_ids" not in vals or not (
            [
                item
                for item in vals["item_ids"]
                if item[0] != 0  # in a create, one2many create command
                or not is_useless_item_vals(item[2])
            ]
        ):
            vals["item_ids"] = [(6, 0, [])]
        return super(ProductPricelist, self).create(vals)
