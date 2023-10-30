# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from odoo.addons.alc_cerberus_utils import utils

from .models.alc_eshop_product_on_order import AlcEshopProductOnOrder


class CancelProductOnOrderRequest(BaseModel):
    quantity: float


class CancelProductOnOrderResponse(BaseModel):
    status: bool
    error_msg: str | None = Field(
        None, description="Error message in case of status=False "
    )


class ProductFamily(Enum):
    meds = "meds"
    food = "food"
    equipment = "equipment"


class ProductOnOrder(BaseModel):
    has_backorder: bool
    description: str
    qty_to_deliver: float
    order_ref: str
    qty_in_backorder: float
    order_date: datetime
    product_id: int
    order_line_id: int
    qty_ordered: float
    customer_ref: str | None = None
    is_mto: bool
    product_family: ProductFamily | None = None

    @classmethod
    def from_alc_eshop_product_on_order(
        cls, row: AlcEshopProductOnOrder
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        product_family = None
        if row["is_food"]:
            product_family = ProductFamily.food
        if row["is_meds"]:
            product_family = ProductFamily.meds
        if row["is_equipment"]:
            product_family = ProductFamily.equipment
        return cls(
            has_backorder=row.has_backorder,
            description=row.description,
            qty_to_deliver=row.qty_to_deliver,
            order_ref=row.order_ref,
            qty_in_backorder=row.qty_backorder,
            order_date=utils.odoo_dt_to_dt_utc(row.order_id.date_order),
            product_id=row.product_id.id,
            order_line_id=row.order_line_id.id,
            qty_ordered=row.qty_ordered,
            customer_ref=row.customer_ref or None,
            is_mto=row.is_mto,
            product_family=product_family,
        )


class Restrict(Enum):
    has_backorder = "has_backorder"
    is_mto = "is_mto"


class ProductOnOrderList(BaseModel):
    data: list[ProductOnOrder] | None = None
    size: int | None = None
