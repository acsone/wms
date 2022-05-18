# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopfloorSchemaAction(Component):

    _inherit = "shopfloor.schema.action"

    def picking(self, with_pickings=False):
        schema = super(ShopfloorSchemaAction, self).picking()
        schema["delivery_round"] = self._schema_dict_of(
            self.delivery_round(), required=False
        )
        return schema

    def delivery_round(self):
        return {
            "code": {"required": False, "type": "string"},
            "name": {"required": False, "type": "string"},
        }
