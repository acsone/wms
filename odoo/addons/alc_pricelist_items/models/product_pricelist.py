# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.product.models.product_pricelist import Pricelist


class ProductPricelist(Pricelist):
    def button_display_items(self):
        self.ensure_one()
        return {
            "name": _("Price list items"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "product.pricelist.item",
            "domain": [("pricelist_id", "=", self.id)],
            "context": {"default_pricelist_id": self.id},
            "target": "current",
        }
