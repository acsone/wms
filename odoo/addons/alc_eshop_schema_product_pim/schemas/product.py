# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    promo_bag: bool | None = None
    sterile: bool | None = None
    fabric: bool | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.promo_bag = odoo_rec.promo_bag
        obj.sterile = odoo_rec.sterile
        obj.fabric = odoo_rec.fabric
        return obj
