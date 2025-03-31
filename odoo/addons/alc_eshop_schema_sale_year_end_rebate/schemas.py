# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from typing import Annotated

from pydantic import Field

from odoo.addons.shopinvader_schema_sale.schemas import sale


class Sale(sale.Sale, extends=True):
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

    @classmethod
    def from_sale_order(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order(odoo_rec)
        res.rebate_accrued_total_amount = odoo_rec.rebate_accrued_total_amount
        res.rebate_accrued_total_max_amount = odoo_rec.rebate_accrued_total_max_amount
        res.rebate_accrued_amount = odoo_rec.rebate_accrued_amount
        res.rebate_accrued_max_amount = odoo_rec.rebate_accrued_max_amount
        res.rebate_potential_amount = odoo_rec.rebate_potential_amount
        res.rebate_potential_max_amount = odoo_rec.rebate_potential_max_amount
        return res
