# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    @api.multi
    def display_items(self):

        self.ensure_one()
        action = {
            "name": _("Price list items"),
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "product.pricelist.item",
            "search_view_id": self.env.ref(
                "alc_pricelist_items.product_pricelist_item_search_view"
            ).id,
            "view_id": self.env.ref(
                "alc_pricelist_items.view_product_pricelist_item_tree"
            ).id,
            "domain": [("pricelist_id", "=", self.id)],
            "target": "current",
        }
        return action
