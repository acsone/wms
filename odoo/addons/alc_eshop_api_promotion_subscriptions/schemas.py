# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from pydantic import BaseModel


class SubscriptionRequest(BaseModel, extra="ignore"):
    product_id: int


class SubscriptionStatus(BaseModel):
    status: bool


class Subscription(BaseModel):
    product_id: int


class SubscriptionList(BaseModel):
    data: list[Subscription]
    size: int
