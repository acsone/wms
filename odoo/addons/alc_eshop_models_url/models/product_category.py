# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product_url.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):
    def _generate_url_key(self, referential, lang):
        url_key = super()._generate_url_key(referential, lang)
        if not self.parent_id or not self.parent_id.active:
            # we are at the root category. We must add the prefix
            # For alcyon we remove the first level of category
            return "c"
        return url_key
