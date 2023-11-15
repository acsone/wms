# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)

from .uom import Uom


class ProductProduct(BaseProductProduct, extends=True):
    dimensional_uom_id: Uom | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.dimensional_uom_id = (
            Uom.from_uom_uom(odoo_rec.dimensional_uom_id)
            if odoo_rec.dimensional_uom_id
            else None
        )
        return obj
