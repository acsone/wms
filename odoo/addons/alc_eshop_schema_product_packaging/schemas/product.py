# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    unit_in_shrink_wrap: int = 0

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.unit_in_shrink_wrap = (
            odoo_rec.unit_in_shrink_wrap if odoo_rec.unit_in_shrink_wrap else 0
        )
        return obj
