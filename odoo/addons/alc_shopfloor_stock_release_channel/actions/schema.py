# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopfloorSchemaAction(Component):

    _inherit = "shopfloor.schema.action"

    def picking(self, with_pickings=False):
        schema = super().picking()
        schema["release_channel"] = self._schema_dict_of(
            self.release_channel(), required=False
        )
        return schema

    def release_channel(self):
        return {
            "code": {"required": False, "type": "string"},
            "name": {"required": False, "type": "string"},
        }
