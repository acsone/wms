# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)

from .product_storage_temperature import ProductStorageTemperature


class ProductProduct(BaseProductProduct, extends=True):
    storage_temperature_id: ProductStorageTemperature | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.storage_temperature_id = (
            ProductStorageTemperature.from_product_storage_temperature(
                odoo_rec.storage_temperature_id
            )
            if odoo_rec.storage_temperature_id
            else None
        )
        return obj
