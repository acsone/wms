# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date
from enum import Enum
from typing import Optional

from odoo.addons.delivery.models.delivery_carrier import DeliveryCarrier
from odoo.addons.stock.models.stock_picking import Picking

from .base_model import BaseModel


class Carrier(Enum):
    ALCYON = "ALCYON"
    GLS_BE = "GLS_BE"

    @classmethod
    def from_delivery_carrier(
        cls, carrier: DeliveryCarrier | None | bool
    ) -> Optional["Carrier"]:
        if not carrier:
            return None
        if carrier.name == "ALCYON":
            return cls.ALCYON
        if carrier.name == "GLS_BE":
            return cls.GLS_BE
        return None


class Delivery(BaseModel):
    carrier: Carrier | None = None
    delivery_date: date | None = None
    tracking_reference: str | None = None

    @classmethod
    def from_stock_picking(cls, stock_picking: Picking) -> "Delivery":
        return cls.model_construct(
            tracking_reference=stock_picking.carrier_tracking_ref or None,
            delivery_date=stock_picking._get_delivery_date(),
            carrier=Carrier.from_delivery_carrier(stock_picking.carrier_id)
            if stock_picking.carrier_id
            else None,
        )
