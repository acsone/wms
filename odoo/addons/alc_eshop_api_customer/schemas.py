# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import annotations

from extendable_pydantic.models import StrictExtendableBaseModel

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.shopinvader_schema_address.schemas import Address


class CustomerData(StrictExtendableBaseModel):
    data: Address

    @classmethod
    def from_res_partner(cls, partner: Partner):
        return cls.model_construct(data=Address.from_res_partner(partner))


class SalesPerson(StrictExtendableBaseModel):
    name: str
    address: Address

    @classmethod
    def from_res_partner(
        cls, partner: Partner
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls.model_construct(
            name=partner.name,
            address=Address.from_res_partner(partner),
        )


class CustomerUpdate(StrictExtendableBaseModel):
    opt_out: bool

    def to_res_partner(self):
        return {"opt_out": self.opt_out}
