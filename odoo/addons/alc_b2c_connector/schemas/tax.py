# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.account.models.account_tax import AccountTax

from . import amount_type
from .base_model import BaseModel


class Tax(BaseModel):
    amount_type: amount_type.AmountType
    amount: float
    name: str

    @classmethod
    def from_account_tax(cls, tax: AccountTax) -> "Tax":
        return cls.model_construct(
            amount_type=amount_type.AmountType(tax.amount_type),
            amount=tax.amount,
            name=tax.name,
        )
