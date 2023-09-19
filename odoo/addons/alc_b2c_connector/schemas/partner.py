# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.base.models.res_partner import Partner

from . import country_code as country, partner_title
from .base_model import BaseModel


class PartnerCommon(BaseModel):
    street2: str | None = None
    phone: str | None = None
    street: str | None = None
    name2: str | None = None
    country_code: country.CountryCode | None = None
    city: str | None = None
    zip: str | None = None
    title: partner_title.Title | None = None
    mobile: str | None = None
    note: str | None = None
    email: str | None = None

    @classmethod
    def from_res_partner(cls, res_partner: Partner) -> "PartnerCommon":
        return cls.model_construct(
            street2=res_partner.street2 or None,
            phone=res_partner.phone or None,
            street=res_partner.street or None,
            name2=res_partner.suite or None,
            country_code=country.CountryCode.from_res_country(res_partner.country_id),
            city=res_partner.city or None,
            zip=res_partner.zip or None,
            title=partner_title.Title.from_partner_title(res_partner.title),
            mobile=res_partner.mobile or None,
            note=res_partner.comment or None,
            email=res_partner.email or None,
        )


class PartnerRequest(PartnerCommon):
    first_name: str | None = None
    last_name: str | None = None


class PartnerResponse(PartnerCommon):
    id: str
    name: str

    @classmethod
    def from_res_partner(cls, res_partner: Partner) -> "PartnerResponse":
        obj = super().from_res_partner(res_partner)
        obj.id = res_partner._b2c_ref_to_b2c_id(res_partner.ref)
        obj.name = res_partner.name
        return obj


class PartnerSaleOrderRequest(PartnerRequest):
    id: str
