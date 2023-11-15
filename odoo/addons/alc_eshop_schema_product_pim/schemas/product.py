# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    promo_bag: bool | None = None
    sterile: bool | None = None
    fabric: bool | None = None
    description_shop_short: str | None = None
    description_shop_long: str | None = None
    class_amcra: str | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.promo_bag = odoo_rec.promo_bag
        obj.sterile = odoo_rec.sterile
        obj.fabric = odoo_rec.fabric
        obj.description_shop_short = (
            odoo_rec.description_shop_short if odoo_rec.description_shop_short else None
        )
        obj.description_shop_long = (
            odoo_rec.description_shop_long if odoo_rec.description_shop_long else None
        )
        obj.class_amcra = odoo_rec.class_amcra if odoo_rec.class_amcra else None
        return obj
