# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel


class AccountTax(StrictExtendableBaseModel):
    id: int
    name: str
    amount: float = 0.0

    @classmethod
    def from_account_tax(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.display_name,
            amount=odoo_rec.amount,
        )
