# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class YearCount(BaseModel):
    food: int
    meds: int
    equipment: int


class FiveYearsResponse(BaseModel):
    data: list[YearCount] = []
    size: int


class MonthlyOrderedResponse(BaseModel):
    average: float
    months: Annotated[
        dict[date, float],
        Field(
            description="A month / average qty mapping ordered by month (older first)"
        ),
    ]


class ProductFamily(Enum):
    meds = "meds"
    food = "food"
    equipment = "equipment"


class OrderedProductInfo(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    date_last_ordered: datetime
    product_family: ProductFamily | None = None
    product_id: int
    ordered_count: int


class TopOrderedResponse(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    data: list[OrderedProductInfo] = []
    size: int
