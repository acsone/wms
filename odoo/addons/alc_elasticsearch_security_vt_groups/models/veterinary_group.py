# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from slugify import slugify

from odoo import api
from odoo.models import Model


class VeterinaryGroup(Model):

    _name = "veterinary.group"
    _inherit = ["veterinary.group", "elasticsearch.role.mixin"]

    @api.model
    def _get_inverse_field_name(self):
        return "vt_group_id"

    def _get_role_name(self):
        return slugify(f"g{self.id}")

    def _get_role_body(self):
        body = """{
            "index_permissions":[
                {
                    "index_patterns":["alc_shopinvader_variant_*"],
                    "fls": ["vt_groups.%s"]
                }
            ]
            }
        """
        return body % self.id

    def _get_vals(self):
        vals = super()._get_vals()
        vals["extra_backend_roles"] = self._get_role_name()
        return vals
