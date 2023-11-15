# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    link_info: str | None = None
    link_notice: str | None = None
    link_video: str | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.link_info = odoo_rec.link_info if odoo_rec.link_info else None
        obj.link_notice = odoo_rec.link_notice if odoo_rec.link_notice else None
        obj.link_video = odoo_rec.link_video if odoo_rec.link_video else None
        return obj
