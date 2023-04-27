# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Type

from pydantic.utils import GetterDict

from ...utils import BaseModel
from . import delivery, partner, sale_line


class SaleOrderState(Enum):
    draft = "draft"
    sale = "sale"
    cancel = "cancel"
    delivery = "delivery"


class SaleOrderCommon(BaseModel):
    date: Optional[date]
    carrier: Optional[delivery.Carrier] = None
    id: str


class SaleOrderResponse(SaleOrderCommon):
    confirmation_date: Optional[datetime]
    lines: List[sale_line.SaleLineResponse]
    deliveries: Optional[List[delivery.Delivery]] = None
    state: SaleOrderState
    ref: str
    recipient: Optional[partner.PartnerResponse] = None
    customer_ref: str

    class Config:
        orm_mode = True

    @classmethod
    def _decompose_class(cls: Type["Model"], obj: Any) -> GetterDict:  # noqa: F821
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
    lines: List[sale_line.SaleLineRequest]
    recipient: Optional[partner.PartnerSaleOrderRequest] = None
    customer_ref: str

    def _convert_to_write(self):
        return {key: value for key, value in dict(self).items() if value}


class SaleOrderUpdateRequest(BaseModel):
    recipient: Optional[partner.PartnerSaleOrderRequest] = None
    lines: Optional[List[sale_line.SaleLineRequest]] = None

    def _convert_to_write(self):
        return {key: value for key, value in dict(self).items() if value}
