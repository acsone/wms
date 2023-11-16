# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from extendable_pydantic.models import StrictExtendableBaseModel

from odoo.addons.account_payment_mode.models import account_payment_mode
from odoo.addons.account_payment_sale.models import sale_order
from odoo.addons.shopinvader_schema_sale.schemas import sale


class SalePaymentMode(StrictExtendableBaseModel):
    id: int
    name: str

    @classmethod
    def from_account_payment_mode(
        cls, odoo_rec: account_payment_mode.AccountPaymentMode
    ) -> self | None:  # noqa: F821  pylint: disable=undefined-variable
        if not odoo_rec:
            return None
        return cls.model_construct(id=odoo_rec.id, name=odoo_rec.name)


class SalePayment(StrictExtendableBaseModel):
    mode: SalePaymentMode | None = None

    @classmethod
    def from_sale_order(
        cls, odoo_rec: sale_order.SaleOrder
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls.model_construct(
            mode=SalePaymentMode.from_account_payment_mode(odoo_rec.payment_mode_id)
        )


class Sale(sale.Sale, extends=True):
    payment: SalePayment | None = None

    @classmethod
    def from_sale_order(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order(odoo_rec)
        res.payment = SalePayment.from_sale_order(odoo_rec)
        return res
