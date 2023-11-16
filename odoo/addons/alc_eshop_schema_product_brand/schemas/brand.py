# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product_brand.schemas.brand import (
    ProductBrand as BaseProductBrand,
)


class ProductBrand(BaseProductBrand, extends=True):
    image_url: str | None = None

    @classmethod
    def from_product_brand(cls, odoo_rec):
        obj = super().from_product_brand(odoo_rec)
        obj.image_url = (
            odoo_rec.image.url if odoo_rec.image and odoo_rec.image.url else None
        )
        return obj
