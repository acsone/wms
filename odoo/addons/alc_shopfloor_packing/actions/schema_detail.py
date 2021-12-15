# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class ShopfloorSchemaDetailAction(Component):
    _inherit = "shopfloor.schema.detail.action"

    def pack_picking_detail(self):
        schema = self.picking_detail()
        schema["scanned_packs"] = {"type": "list", "schema": {"type": "integer"}}
        return schema
