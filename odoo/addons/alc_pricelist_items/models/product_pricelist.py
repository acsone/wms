# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    @api.multi
    def display_items(self):
        tree_view_id = self.env.ref(
            "alc_pricelist_items.view_product_pricelist_item_tree"
        ).id
        form_view_id = self.env.ref("product.product_pricelist_item_form_view").id
        search_view_id = self.env.ref(
            "alc_pricelist_items.product_pricelist_item_search_view"
        ).id
        self.ensure_one()
        action = {
            "name": _("Price list items"),
            "type": "ir.actions.act_window",
            "view_mode": "tree, form",
            "res_model": "product.pricelist.item",
            "search_view_id": search_view_id,
            "views": [(tree_view_id, "tree"), (form_view_id, "form")],
            "domain": [("pricelist_id", "=", self.id)],
            "context": {"default_pricelist_id": self.id},
            "target": "current",
        }
        return action
