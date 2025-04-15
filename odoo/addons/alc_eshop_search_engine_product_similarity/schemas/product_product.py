# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    characteristics_vector: list[float] | None
    description_vector: list[float] | None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.characteristics_vector = (
            odoo_rec.characteristics_vector
            and odoo_rec.characteristics_vector.to_list()
            or None
        )
        obj.description_vector = (
            odoo_rec.description_vector
            and odoo_rec.description_vector.to_list()
            or None
        )
        return obj
