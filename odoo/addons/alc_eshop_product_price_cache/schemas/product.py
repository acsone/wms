# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from extendable_pydantic.models import StrictExtendableBaseModel

from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class PriceCacheItem(StrictExtendableBaseModel):
    id: int | None
    date_start: date | None
    date_end: date | None
    discount: float | None = None
    price: float | None = None
    min_quantity: int = 0
    exclusive: bool = False


class ProductProduct(BaseProductProduct, extends=True):
    price: dict[str, list[PriceCacheItem]] = {}

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.price = odoo_rec.price_cache if odoo_rec.price_cache else {}
        return obj
