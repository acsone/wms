# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)

from .order_mode import OrderMode


class ProductProduct(BaseProductProduct, extends=True):
    order_mode: OrderMode

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.order_mode = odoo_rec.shop_order_mode
        return obj
