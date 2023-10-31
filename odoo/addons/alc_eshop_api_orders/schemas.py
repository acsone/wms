# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from odoo.addons.alc_cerberus_utils import utils


class SaleChannel(Enum):
    phone = "phone"
    mail = "mail"
    fax = "fax"
    web = "web"


class OrderLine(BaseModel):
    qty_delivered: float
    reference: str
    price: float
    line_id: int
    qty_canceled: float
    qty_ordered: float

    @classmethod
    def from_sale_order_line(cls, record):
        return cls(
            qty_delivered=record.qty_delivered,
            reference=record.product_id.default_code,
            price=record.price_reduce_taxexcl,
            line_id=record.id,
            qty_canceled=record.product_qty_canceled,
            qty_ordered=record.product_uom_qty,
        )


class Order(BaseModel):
    state: str
    suite_name: str | None = None
    name: str
    state_label: str | None
    sale_channel: SaleChannel
    customer_ref: str | None = None
    date_order: datetime
    lines: list[OrderLine] = []
    id: int
    amount_total: float

    @classmethod
    def from_sale_order(cls, record):
        field = record._fields["shopinvader_state"]
        state_label = field.convert_to_export(record.shopinvader_state, record)
        return cls(
            id=record.id,
            name=record.name,
            customer_ref=record.client_order_ref or None,
            state=record.state,
            state_label=state_label or None,
            amount_total=record.amount_total,
            date_order=utils.odoo_dt_to_dt_utc(record.date_order),
            lines=[OrderLine.from_sale_order_line(line) for line in record.order_line],
            sale_channel=SaleChannel(record.sale_channel_id.code),
            suite_name=record.suite_name or None,
        )


class OrderList(BaseModel):
    data: list[Order]
    size: int
