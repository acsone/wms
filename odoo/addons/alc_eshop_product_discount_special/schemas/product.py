# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)

from .product_discount_special import ProductDiscountSpecial


class ProductProduct(BaseProductProduct, extends=True):
    specials: list[ProductDiscountSpecial | None] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.specials = (
            [
                ProductDiscountSpecial.from_product_discount_special(discount)
                for discount in odoo_rec.product_discount_special_ids
            ]
            if odoo_rec.product_discount_special_ids
            else []
        )
        return obj
