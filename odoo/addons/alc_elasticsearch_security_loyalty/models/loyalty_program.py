# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from slugify import slugify

from odoo import api
from odoo.models import Model


class LoyaltyProgram(Model):

    _name = "loyalty.program"
    _inherit = ["loyalty.program", "elasticsearch.role.mixin"]

    @api.model
    def _get_inverse_field_name(self):
        return "loyalty_program_id"

    @api.model
    def _get_role_name_fields(self):
        return ["id"]

    def _get_role_name(self):
        return slugify(f"lp{self.id}")

    def _get_role_body(self):
        body = {
            "index_permissions": [
                {
                    "index_patterns": ["alc_loyalty_program_*"],
                    "dls": f'{{"term": {{"id": {self.id}}}}}',
                    "allowed_actions": ["read"],
                }
            ]
        }
        body = json.dumps(body)
        return body

    def _get_vals(self):
        vals = super()._get_vals()
        vals["extra_backend_roles"] = self._get_role_name()
        return vals
