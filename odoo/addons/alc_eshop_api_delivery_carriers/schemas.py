# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from pydantic import BaseModel

from odoo.addons.delivery.models import delivery_carrier


class DeliveryCarrier(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    id: int
    name: str

    @classmethod
    def from_delivery_carrier(
        cls, record: delivery_carrier.DeliveryCarrier
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            id=record.id,
            name=record.name,
        )


class DeliveryCarrierList(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    data: list[DeliveryCarrier]

    @classmethod
    def from_delivery_carrier(
        cls, record: delivery_carrier.DeliveryCarrier
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(data=[DeliveryCarrier.from_delivery_carrier(rec) for rec in record])
