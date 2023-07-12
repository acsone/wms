# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from enum import Enum

from pydantic.utils import GetterDict

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
    carrier: delivery.Carrier | None = None
    id: int


class SaleOrderResponse(SaleOrderCommon):
    confirmation_date: datetime | None
    lines: list[sale_line.SaleLineResponse]
    deliveries: list[delivery.Delivery] | None = None
    state: SaleOrderState
    ref: str
    recipient: partner.PartnerResponse | None = None
    customer_ref: str

    class Config:
        orm_mode = True

    @classmethod
    def _decompose_class(
        cls: type["SaleOrderResponse"], obj: SaleOrder
    ) -> GetterDict:  # noqa: F821
        state = obj.b2c_state
        res = {
            "id": obj.b2c_ref,
            "customer_ref": obj.partner_id.ref,
            "date": obj.date_order,
            "recipient": partner.PartnerResponse.from_orm(obj.partner_id),
            "ref": obj.name,
            "state": state,
            "confirmation_date": obj.date_order
            if obj.state in ("sale", "done")
            else None,
            "lines": [
                sale_line.SaleLineResponse.from_orm(line)
                for line in obj.order_line.filtered("b2c_ref")
            ],
        }
        if state == "delivery":
            res["deliveries"] = [
                delivery.Delivery.from_orm(ship)
                for ship in obj.mapped("picking_ids").filtered(
                    lambda p: p.picking_type_code == "outgoing"
                )
            ]
        return res


class SaleOrderCreateRequest(SaleOrderCommon):
    lines: list[sale_line.SaleLineRequest]
    recipient: partner.PartnerSaleOrderRequest | None = None
    customer_ref: str


class SaleOrderUpdateRequest(BaseModel):
    recipient: partner.PartnerSaleOrderRequest | None = None
    lines: list[sale_line.SaleLineRequest] | None = None
