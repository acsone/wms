# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class LoyaltyProgram(BaseModel):
    id: int
    name: str
    program_type: str
    date_from: date
    date_to: date

    @classmethod
    def from_loyalty_program(
        cls, rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            id=rec.id,
            name=rec.name,
            program_type=rec.program_type,
            date_from=rec.date_from,
            date_to=rec.date_to,
        )


class LoyaltyCard(BaseModel):
    id: int
    program: LoyaltyProgram
    points: float
    accrued_points: float
    max_points: float
    max_accrued_points: float

    @classmethod
    def from_loyalty_card(
        cls, rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            id=rec.id,
            program=LoyaltyProgram.from_loyalty_program(rec.program_id),
            points=rec.points,
            accrued_points=rec.accrued_points,
            max_points=rec.max_points,
            max_accrued_points=rec.max_accrued_points,
        )


class LoyaltyCardHistory(BaseModel):
    order_id: int
    order_ref: str
    date_order: datetime
    points: float
    max_points: float
    accrued_points: float
    max_accrued_points: float

    @classmethod
    def from_sale_order_coupon_point(
        cls, rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            order_id=rec.order_id.id,
            order_ref=rec.order_id.name,
            date_order=rec.order_id.date_order,
            points=rec.points,
            max_points=rec.max_points,
            accrued_points=rec.accrued_points,
            max_accrued_points=rec.max_accrued_points,
        )
