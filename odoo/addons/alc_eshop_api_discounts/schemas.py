# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from odoo.addons.alc_supplier_promotion.models.product_supplierinfo import (
    ProductSupplierInfo,
)


class Discount(BaseModel):
    ratio_main_product: int | None = None
    ratio_promotional_product: int | None = None
    reference: str
    date_end: date
    date_start: date
    discount_sale: float | None = None
    is_promotion: bool
    is_sale_discount: bool

    @classmethod
    def from_product_supplierinfo(cls, record: ProductSupplierInfo):
        return cls(
            ratio_main_product=record.ratio_main_product,
            ratio_promotional_product=record.ratio_promotional_product,
            reference=record.product_tmpl_id.default_code,
            date_end=record.date_end,
            date_start=record.date_start,
            discount_sale=record.discount_sale,
            is_promotion=record.is_promotion,
            is_sale_discount=record.is_sale_discount,
        )


class DiscountList(BaseModel):
    data: list[Discount]
    size: int
