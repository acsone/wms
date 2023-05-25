# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from typing import Any

from odoo.addons.alc_b2c_connector.services.utils import (  # pylint: disable=odoo-addons-relative-import
    BaseModel,
)

from pydantic.utils import GetterDict

from . import tax


class Product(BaseModel):
    sku: str | None
    create_date: datetime
    name: str
    price: float
    eans: list[str] | None
    cnk: str | None
    taxes: list[tax.Tax] | None
    quantity: float

    class Config:
        orm_mode = True

    @classmethod
    def _decompose_class(cls: type["Product"], obj: Any) -> GetterDict:
        res = {
            "name": obj.name,
            "sku": obj.default_code or None,
            "cnk": obj.cnk_code or None,
            "price": obj.list_price,
            "create_date": obj.create_date,
            "quantity": obj.immediately_usable_qty,
            "eans": [],
        }
        ean = obj.barcode
        if ean:
            res["eans"] = [ean]
        taxes = []
        for tax_ in obj.taxes_id:
            taxes.append(
                {
                    "name": tax_.name,
                    "amount": tax_.amount,
                    "amount_type": tax_.amount_type,
                }
            )
        res["taxes"] = taxes
        return res
