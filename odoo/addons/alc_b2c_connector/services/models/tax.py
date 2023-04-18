# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from pydantic import BaseModel

from . import amount_type


class Tax(BaseModel):
    amount_type: amount_type.AmountType
    amount: float
    name: str
