# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    characteristics_vector: list[float]
    description_vector: list[float]

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super(ProductProduct, cls).from_product_product(odoo_rec)  # noqa: UP008

        characteristics_vector = str(odoo_rec.characteristics_vector.value.tolist())
        description_vector = str(odoo_rec.description_vector.value.tolist())

        return cls.model_construct(
            **obj.model_dump(),
            characteristics_vector=characteristics_vector,
            description_vector=description_vector,
        )
