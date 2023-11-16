# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from pydantic import BaseModel

from odoo.addons.alc_eshop_schema_sale_delivery.schemas import DeliveryMethod
from odoo.addons.delivery.models import delivery_carrier


class DeliveryMethodList(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    data: list[DeliveryMethod]

    @classmethod
    def from_delivery_carrier(
        cls, record: delivery_carrier.DeliveryCarrier
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(data=[DeliveryMethod.from_delivery_carrier(rec) for rec in record])
