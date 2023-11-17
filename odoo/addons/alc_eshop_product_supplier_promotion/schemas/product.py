# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    supplier_promotion: list[dict[str, str | int | float | dict[str, str]]] = []
    supplier_promotion_veterinary: list[
        dict[str, str | int | float | dict[str, str]]
    ] = []
    supplier_discount: list[dict[str, str | int | float | dict[str, str]]] = []

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.supplier_promotion = (
            odoo_rec.supplier_promotion_json if odoo_rec.supplier_promotion_json else []
        )
        obj.supplier_promotion_veterinary = (
            odoo_rec.supplier_promotion_json_for_veterinaries
            if odoo_rec.supplier_promotion_json_for_veterinaries
            else []
        )
        obj.supplier_discount = (
            odoo_rec.supplier_discount_json if odoo_rec.supplier_discount_json else []
        )
        return obj
