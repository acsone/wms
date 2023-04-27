# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date
from enum import Enum
from typing import Any, Optional, Type

from pydantic.utils import GetterDict

from odoo.addons.alc_b2c_connector.utils import (  # pylint: disable=odoo-addons-relative-import
    BaseModel,
)


class Carrier(Enum):
    ALCYON = "ALCYON"
    GLS_BE = "GLS_BE"


class Delivery(BaseModel):
    carrier: Optional[Carrier] = None
    delivery_date: Optional[date] = None
    tracking_reference: Optional[str] = None

    class Config:
        orm_mode = True

    @classmethod
    def _decompose_class(cls: Type["Model"], obj: Any) -> GetterDict:  # noqa: F821
        return {
            "tracking_reference": obj.carrier_tracking_ref or None,
            "delivery_date": obj._get_delivery_date(),
            "carrier": obj.carrier_id.name or None,
        }
