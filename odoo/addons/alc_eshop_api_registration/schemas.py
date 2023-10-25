# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from enum import Enum

from pydantic import BaseModel

from odoo import api


class Function(Enum):
    function_nurse = "function_nurse"
    function_veterinary = "function_veterinary"
    function_student = "function_student"
    function_supplier = "function_supplier"
    function_wholesaler = "function_wholesaler"
    function_pharmacist = "function_pharmacist"


class Title(Enum):
    title_mrs = "title_mrs"
    title_mr = "title_mr"
    title_miss = "title_miss"
    title_dr = "title_dr"


class ClienteleEnum(Enum):
    livestock = "livestock"
    equine = "equine"
    pet = "pet"
    exotic = "exotic"


class RegistrationRqst(BaseModel):
    function: Function
    apb_authorization: str | None = None
    fax: str | None = None
    zip: str
    vet_subscription_number: str | None = None
    firstname: str
    title: Title
    mobile: str | None = None
    lastname: str
    clientele: list[ClienteleEnum]
    comment: str | None = None
    vat: str | None = None
    street: str
    city: str
    company_name: str | None = None
    street2: str | None = None
    country_name: str
    email: str | None = None
    vet_depot_number: str | None = None
    opt_out: bool

    def to_alc_registration_create(self, env: api.Environment):
        ret = {}
        if self.function:
            value = self.function.value
            key = "function_assistant" if value == "function_nurse" else value
            ret["occupation"] = key.replace("function_", "")
        if self.apb_authorization:
            ret["apb_authorization"] = self.apb_authorization
        if self.fax:
            ret["fax"] = self.fax
        ret["zip"] = self.zip
        ret["vet_subscription_number"] = self.vet_subscription_number

        first_name = self.firstname
        last_name = self.lastname
        ret["name"] = f"{first_name} {last_name}".strip()
        ret["title"] = self.title_to_id(env)
        if self.mobile:
            ret["mobile"] = self.mobile
        ret["clientele"] = ",".join(c.value for c in self.clientele)
        if self.comment:
            ret["comment"] = self.comment
        if self.vat:
            ret["vat"] = self.vat
        ret["street"] = self.street
        ret["city"] = self.city
        if self.company_name:
            ret["company_name"] = self.company_name
        if self.street2:
            ret["street2"] = self.street2
        ret["country_name"] = self.country_name
        if self.email:
            ret["email"] = self.email
        ret["vet_depot_number"] = self.vet_depot_number
        ret["opt_out"] = self.opt_out
        return ret

    def title_to_id(self, env: api.Environment):
        keys = {
            "title_mrs": "madam",
            "title_mr": "mister",
            "title_miss": "miss",
            "title_dr": "doctor",
        }
        title_key = keys[self.title.value]
        return env.ref(f"base.res_partner_title_{title_key}").id


class RegistrationId(BaseModel):
    id: int
