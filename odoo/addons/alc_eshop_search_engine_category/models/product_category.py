# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):
    def shopinvader_category_bind(self):
        indexes = self.env["se.index"].search(
            [("model_id.model", "=", "product.category")]
        )
        self._add_to_index(indexes)

    def shopinvader_category_unbind(self):
        indexes = self.env["se.index"].search(
            [("model_id.model", "=", "product.category")]
        )
        self._remove_from_index(indexes)
