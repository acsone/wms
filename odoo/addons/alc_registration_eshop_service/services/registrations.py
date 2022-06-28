# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class RegistrationService(Component):
    _inherit = ["standard.service.mixin"]
    _name = "registration.service"
    _collection = "shopinvader.backend"
    _usage = "registrations"

    @property
    def model(self):
        return self.env["alc.registration"]

    @restapi.method(
        [(["/"], "POST")],
        input_param=restapi.CerberusValidator("_input_schema"),
        output_param=restapi.CerberusValidator("_output_schema"),
        auth="public_or_default",
    )
    def submit(self, **params):
        vals = self._process_params(params, "input")
        registration = self.model.sudo().create(vals)  # public user needs sudo
        return self._process_records(registration, "output")[0]

    def _map_input_name(self, params):
        firstname = params.pop("firstname", "")
        lastname = params.pop("lastname", "")
        params["name"] = " ".join((firstname, lastname)).strip()
        return params

    def _map_input_title_id(self, params):
        title_str = params.get("title")
        if title_str:
            keys = {
                "title_mrs": "madam",
                "title_mr": "mister",
                "title_miss": "miss",
                "title_dr": "doctor",
            }
            title_key = keys[title_str]
            title = self.env.ref("base.res_partner_title_%s" % title_key)
            params["title"] = title.id
        return params

    def _map_input_function_occupation(self, params):
        value = params.get("function")
        if value:
            key = "function_assistant" if value == "function_nurse" else value
            params["occupation"] = key.replace("function_", "")
        return params

    def _input_schema(self):
        return self._get_schema("input")

    def _output_schema(self):
        return self._get_schema("output")

    def _get_schema_generator(self):
        return {
            "firstname": {
                "type": "string",
                "required": True,
                "nullable": False,
                "input": {"map": "_map_input_name"},
            },
            "lastname": {
                "type": "string",
                "required": True,
                "nullable": False,
                "input": {"map": "_map_input_name"},
            },
            "title": {
                "type": "string",
                "required": True,
                "nullable": False,
                "allowed": ["title_mrs", "title_mr", "title_miss", "title_dr"],
                "input": {"map": "_map_input_title_id", "mapper_keep": True},
            },
            "company_name": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "function": {
                "type": "string",
                "required": True,
                "nullable": False,
                "allowed": [
                    "function_nurse",
                    "function_veterinary",
                    "function_student",
                    "function_supplier",
                    "function_wholesaler",
                    "function_pharmacist",
                ],
                "input": {"map": "_map_input_function_occupation"},
            },
            "clientele": {
                "type": "string",
                "required": True,
                "nullable": False,
                "allowed": self.model._fields["clientele"].get_values(self.env),
                "input": {},
            },
            "vat": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "vet_depot_number": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "vet_subscription_number": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "apb_authorization": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "comment": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "street": {
                "type": "string",
                "required": True,
                "nullable": False,
                "input": {},
            },
            "street2": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "zip": {
                "type": "string",
                "required": True,
                "nullable": False,
                "input": {},
            },
            "city": {
                "type": "string",
                "required": True,
                "nullable": False,
                "input": {},
            },
            "country_name": {
                "type": "string",
                "required": True,
                "nullable": False,
                "input": {},
            },
            "opt_out": {
                "type": "boolean",
                "required": True,
                "nullable": False,
                "input": {},
            },
            "fax": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "mobile": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "email": {
                "type": "string",
                "required": False,
                "nullable": True,
                "input": {},
            },
            "id": {
                "type": "integer",
                "required": True,
                "nullable": False,
                "parser": "id",
                "output": {},
            },
        }
