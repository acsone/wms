# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_multi_category.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ShopinvaderProduct(ProductTemplateBase):
    def _get_categories(self):
        categories = super()._get_categories()
        return categories.filtered(lambda c: c.is_web)
