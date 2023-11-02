# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from enum import Enum
from typing import Annotated

from extendable_pydantic.models import StrictExtendableBaseModel
from pydantic import Field

from odoo.addons.shopinvader_schema_address import schemas


class AddressType(Enum):
    private = "private"
    contact = "contact"
    delivery = "delivery"
    other = "other"
    invoice = "invoice"


class Country(StrictExtendableBaseModel):
    id: int
    name: str
    code: str

    @classmethod
    def from_res_country(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(id=odoo_rec.id, name=odoo_rec.name, code=odoo_rec.code)


class CountryState(StrictExtendableBaseModel):
    id: int
    name: str
    code: str | None = None

    @classmethod
    def from_res_country_state(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(id=odoo_rec.id, name=odoo_rec.name, code=odoo_rec.code or None)


class Address(schemas.Address, extends=True):
    vet_depot_number: str | None = None
    vet_subscription_number: str | None = None
    # The following fields are deprecated and should be removed once
    # the frontend will be adapted to use the new shopinvader_address_api
    country: Annotated[
        Country | None,
        Field(
            description="Prefer use of country_id",
            json_schema_extra={"deprecated": True},
        ),
    ] = None
    state: Annotated[
        CountryState | None,
        Field(
            description="Prefer use of country_id",
            json_schema_extra={"deprecated": True},
        ),
    ]
    display_name: str | None = None
    is_company: bool = False
    address_type: AddressType | None = None
    ref: str | None = None
    opt_out: bool = True
    opt_in: bool = False
    mobile: str | None = None
    vat: str | None = None

    @classmethod
    def from_res_partner(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_res_partner(odoo_rec)
        res.vet_depot_number = odoo_rec.vet_depot_number or None
        res.vet_subscription_number = odoo_rec.vet_subscription_number or None
        res.country = (
            Country.from_res_country(odoo_rec.country_id)
            if odoo_rec.country_id
            else None
        )
        res.state = (
            CountryState.from_res_country_state(odoo_rec.state_id)
            if odoo_rec.state_id
            else None
        )
        res.display_name = odoo_rec.display_name or None
        res.is_company = odoo_rec.is_company
        res.address_type = AddressType(odoo_rec.type) if odoo_rec.type else None
        res.ref = odoo_rec.ref or None
        res.opt_out = odoo_rec.opt_out
        res.opt_in = not odoo_rec.opt_out
        res.mobile = odoo_rec.mobile or None
        res.vat = odoo_rec.vat or None
        return res
