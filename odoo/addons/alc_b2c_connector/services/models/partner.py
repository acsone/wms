# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Any

from odoo.addons.alc_b2c_connector.services.utils import (  # pylint: disable=odoo-addons-relative-import
    BaseModel,
)

from pydantic.utils import GetterDict

from . import country_code as country, partner_title


class PartnerCommon(BaseModel):
    street2: str | None
    phone: str | None
    street: str | None
    name2: str | None = None
    country_code: country.CountryCode | None
    city: str | None
    zip: str | None
    title: partner_title.Title | None
    mobile: str | None
    note: str | None
    email: str | None


class PartnerRequest(PartnerCommon):
    first_name: str | None
    last_name: str | None


class PartnerResponse(PartnerCommon):
    id: str
    name: str

    class Config:
        orm_mode = True

    @classmethod
    def _decompose_class(cls: type["Model"], obj: Any) -> GetterDict:  # noqa: F821
        return {
            "id": obj._b2c_ref_to_b2c_id(obj.ref),
            "title": partner_title.Title.from_orm(obj.title),
            "name": obj.name,
            "street": obj.street or None,
            "street2": obj.street2 or None,
            "zip": obj.zip or None,
            "city": obj.city or None,
            "email": obj.email or None,
            "mobile": obj.mobile or None,
            "phone": obj.phone or None,
            "country_code": obj.country_id.code if obj.country_id else None,
            "name2": obj.suite,
            "note": obj.comment or None,
        }


class PartnerSaleOrderRequest(PartnerRequest):
    id: str
