# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Any, Optional, Type

from pydantic.utils import GetterDict

from ...utils import BaseModel


class SaleLineCommon(BaseModel):
    sku: str
    line_id: Optional[str] = None


class SaleLineRequest(SaleLineCommon):
    quantity: float

    def _convert_to_write(self):
        return {key: value for key, value in dict(self).items() if value}


class SaleLineResponse(SaleLineCommon):
    qty_ordered: float
    qty_returned: float
    qty_delivered: float
    qty_cancelled: float
    qty_backorder: float

    class Config:
        orm_mode = True

    @classmethod
    def _decompose_class(cls: Type["Model"], obj: Any) -> GetterDict:  # noqa: F821
        return {
            "line_id": obj.b2c_ref,
            "sku": obj.product_id.default_code,
            "qty_ordered": obj.product_uom_qty,
            "qty_delivered": obj.qty_delivered,
            "qty_cancelled": obj.product_qty_canceled,
            "qty_returned": obj.product_qty_returned,
            "qty_backorder": obj.product_qty_backorder,
        }
