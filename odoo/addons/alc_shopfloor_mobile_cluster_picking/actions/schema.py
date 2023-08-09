# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopfloorSchemaAction(Component):

    _inherit = "shopfloor.schema.action"

    def picking_batch(self, with_pickings=False):
        schema = super().picking_batch(with_pickings=with_pickings)
        schema["device"] = {"required": False, "type": "string"}
        schema["release_channels"] = self._schema_list_of(
            self.release_channel(), required=False
        )
        return schema

    def release_channel(self):
        return {
            "code": {"required": False, "type": "string"},
            "name": {"required": False, "type": "string"},
        }
