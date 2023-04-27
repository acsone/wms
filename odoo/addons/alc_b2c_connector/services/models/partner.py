# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Any, Optional, Type

from pydantic.utils import GetterDict

from odoo.addons.alc_b2c_connector.utils import (  # pylint: disable=odoo-addons-relative-import
    BaseModel,
)

from . import country_code as country, partner_title


class PartnerCommon(BaseModel):
    street2: Optional[str]
    phone: Optional[str]
    street: Optional[str]
    name2: Optional[str] = None
    country_code: Optional[country.CountryCode]
    city: Optional[str]
    zip: Optional[str]
    title: Optional[partner_title.Title]
    mobile: Optional[str]
    note: Optional[str]
    email: Optional[str]


class PartnerRequest(PartnerCommon):
    first_name: Optional[str]
    last_name: Optional[str]


class PartnerResponse(PartnerCommon):
    id: str
    name: str

    class Config:
        orm_mode = True

    @classmethod
    def _decompose_class(cls: Type["Model"], obj: Any) -> GetterDict:  # noqa: F821
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
