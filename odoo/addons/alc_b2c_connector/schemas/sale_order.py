# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from enum import Enum

from ..models.sale_order import SaleOrder
from . import delivery, partner, sale_line
from .base_model import BaseModel


class SaleOrderState(Enum):
    draft = "draft"
    sale = "sale"
    cancel = "cancel"
    delivery = "delivery"


class SaleOrderCommon(BaseModel):
    date: datetime | None
    carrier: delivery.Carrier | None = None  # WHY HERE?
    id: int

    @classmethod
    def from_sale_order(cls, sale_order: SaleOrder) -> "SaleOrderCommon":
        return cls.model_construct(
            id=int(sale_order.b2c_ref),
            date=sale_order.date_order,
            carrier=delivery.Carrier.from_delivery_carrier(sale_order.carrier_id),
        )


class SaleOrderResponse(SaleOrderCommon):
    confirmation_date: datetime | None
    lines: list[sale_line.SaleLineResponse]
    deliveries: list[delivery.Delivery] | None = None
    state: SaleOrderState
    ref: str
    recipient: partner.PartnerResponse | None = None
    customer_ref: str

    @classmethod
    def from_sale_order(cls, sale_order: SaleOrder) -> "SaleOrderResponse":
        obj = super().from_sale_order(sale_order)
        obj.confirmation_date = (
            sale_order.date_order if sale_order.state in ("sale", "done") else None
        )
        obj.lines = [
            sale_line.SaleLineResponse.from_sale_order_line(line)
            for line in sale_order.order_line.filtered("b2c_ref")
        ]
        obj.deliveries = []
        if sale_order.b2c_state == "delivery":
            obj.deliveries = [
                delivery.Delivery.from_stock_picking(ship)
                for ship in sale_order.mapped("picking_ids").filtered(
                    lambda p: p.picking_type_code == "outgoing"
                )
            ]
        obj.state = SaleOrderState(sale_order.b2c_state)
        obj.ref = sale_order.name
        obj.recipient = partner.PartnerResponse.from_res_partner(sale_order.partner_id)
        obj.customer_ref = sale_order.partner_id.ref
        return obj


class SaleOrderCreateRequest(SaleOrderCommon):
    lines: list[sale_line.SaleLineRequest]
    recipient: partner.PartnerSaleOrderRequest | None = None
    customer_ref: str


class SaleOrderUpdateRequest(BaseModel):
    recipient: partner.PartnerSaleOrderRequest | None = None
    lines: list[sale_line.SaleLineRequest] | None = None
