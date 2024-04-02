# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from extendable_pydantic.models import StrictExtendableBaseModel

from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class SupplierInfoTimeFrame(StrictExtendableBaseModel):
    gte: date | None
    lte: date | None


class SupplierPromotion(StrictExtendableBaseModel):
    date_start: date | None
    date_end: date | None
    time_frame: SupplierInfoTimeFrame
    ratio_main_product: int
    ratio_promotional_product: int


class SupplierDiscount(StrictExtendableBaseModel):
    date_start: date | None
    date_end: date | None
    time_frame: SupplierInfoTimeFrame
    discount_sale: float


class ProductProduct(BaseProductProduct, extends=True):
    supplier_promotion: list[SupplierPromotion] = []
    supplier_promotion_veterinary: list[SupplierPromotion] = []
    supplier_discount: list[SupplierDiscount] = []
    supplier_discount_veterinary: list[SupplierDiscount] = []

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
        obj.supplier_discount_veterinary = (
            odoo_rec.supplier_discount_json_for_veterinaries
            if odoo_rec.supplier_discount_json_for_veterinaries
            else []
        )
        return obj
