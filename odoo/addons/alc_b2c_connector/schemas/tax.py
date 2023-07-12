# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import amount_type
from .base_model import BaseModel


class Tax(BaseModel):
    amount_type: amount_type.AmountType
    amount: float
    name: str
