# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    is_mto: bool | None = None
    route_from_categ_ids: list[str] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.is_mto = odoo_rec.is_mto
        obj.route_from_categ_ids = (
            odoo_rec.route_from_categ_ids.mapped("display_name")
            if odoo_rec.route_from_categ_ids
            else []
        )
        return obj
