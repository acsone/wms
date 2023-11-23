# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    def shopinvader_manual_export(self):
        bindings = self._get_bindings()
        if not bindings:
            indexes = self.env["se.index"].search([("model_id.model", "=", self._name)])
            bindings = self._add_to_index(indexes)
        bindings.recompute_json()
        bindings.filtered(lambda b: b.state == "to_export").export_record()
