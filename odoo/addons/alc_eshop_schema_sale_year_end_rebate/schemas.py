# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from typing import Annotated, Any

from pydantic import Discriminator, Field, Tag

from odoo.addons.extendable_fastapi.schemas import StrictExtendableBaseModel
from odoo.addons.shopinvader_schema_sale.schemas import sale


class YearEndRebate(StrictExtendableBaseModel):
    rebate_accrued_amount: Annotated[
        float,
        Field(description="The year end rebate accrued amount for the current order"),
    ] = 0.0
    rebate_accrued_max_amount: Annotated[
        float,
        Field(
            description="The year end rebate accrued max amount for the current order"
        ),
    ] = 0.0
    rebate_potential_amount: Annotated[
        float,
        Field(
            description="The year end rebate potential amount for the current order if all products are delivered"
        ),
    ] = 0.0
    rebate_potential_max_amount: Annotated[
        float,
        Field(
            description="The year end rebate potential max amount for the current order if all products are delivered"
        ),
    ] = 0.0

    program_id: int | None

    @classmethod
    def from_sale_order(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls.model_construct(
            rebate_accrued_amount=odoo_rec.rebate_accrued_amount,
            rebate_accrued_max_amount=odoo_rec.rebate_accrued_max_amount,
            rebate_potential_amount=odoo_rec.rebate_potential_amount,
            rebate_potential_max_amount=odoo_rec.rebate_potential_max_amount,
            program_id=odoo_rec.rfa_program_id.id or None,
        )


class YearEndRebateWithTotal(YearEndRebate):
    rebate_accrued_total_amount: Annotated[
        float,
        Field(
            description="The year end rebate accrued total amount for all the customer's orders"
        ),
    ] = 0.0
    rebate_accrued_total_max_amount: Annotated[
        float,
        Field(
            description="The year end rebate accrued total max amount for all the customer's orders"
        ),
    ] = 0.0

    @classmethod
    def from_sale_order(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        ret = super().from_sale_order(odoo_rec)
        ret.rebate_accrued_total_amount = odoo_rec.rebate_accrued_total_amount
        ret.rebate_accrued_total_max_amount = odoo_rec.rebate_accrued_total_max_amount
        return ret


def year_end_rebate_discriminator(v: Any) -> str | None:
    if isinstance(v, dict):
        if "rebate_accrued_total_amount" in v:
            return "year_end_rebate_with_total"
        if "rebate_accrued_amount" in v:
            return "year_end_rebate"
    if isinstance(v, YearEndRebateWithTotal):
        return "year_end_rebate_with_total"
    if isinstance(v, YearEndRebate):
        return "year_end_rebate"
    return None


class Sale(sale.Sale, extends=True):
    year_end_rebate: Annotated[
        (
            Annotated[YearEndRebate, Tag("year_end_rebate")]
            | Annotated[YearEndRebateWithTotal, Tag("year_end_rebate_with_total")]
        ),
        Discriminator(year_end_rebate_discriminator),
    ]

    @classmethod
    def from_sale_order(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order(odoo_rec)
        rebate_cls = (
            YearEndRebateWithTotal
            if odoo_rec.partner_id._allows_see_total_year_end_rebate()
            else YearEndRebate
        )
        res.year_end_rebate = rebate_cls.from_sale_order(odoo_rec)
        return res
