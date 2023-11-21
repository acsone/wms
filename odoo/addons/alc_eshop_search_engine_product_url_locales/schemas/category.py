# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas import (
    ProductCategory as BaseProductCategory,
)


class ProductCategory(BaseProductCategory, extends=True):
    url_key_locales: dict[str, str] = {}

    @classmethod
    def from_product_category(cls, odoo_rec):
        obj = super().from_product_category(odoo_rec)
        obj.url_key_locales = odoo_rec.url_key_locales
        return obj
