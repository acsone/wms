# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component


class CustomerService(Component):

    _inherit = "shopinvader.customer.service"

    @restapi.method(
        [(["/sales_person"], "GET")],
        output_param=restapi.CerberusValidator("_sales_person_output_schema"),
    )
    def get_sales_person(self):
        partner = (
            self.partner.user_id.partner_id
            or self.shopinvader_backend.sudo().company_id.partner_id
        )
        return {
            "name": partner.name,
            "address": self.partner_serializer._to_json_address(partner),
        }

    def _sales_person_output_schema(self):
        return {
            "name": {"type": "string", "required": True, "nullable": False},
            "address": {
                "type": "dict",
                "schema": self.partner_serializer._json_address_schema,
                "required": True,
                "nullable": False,
            },
        }

    @property
    def partner_serializer(self):
        return self.env["res.partner.serializer"]
