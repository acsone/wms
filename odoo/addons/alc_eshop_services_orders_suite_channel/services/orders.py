# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class OrdersService(Component):

    _inherit = "orders.service"

    def _get_model_schema(self):
        schema = super(OrdersService, self)._get_model_schema()
        schema["sale_channel"] = {"type": "string", "required": True, "nullable": False}
        schema["suite_name"] = {"type": "string", "required": False, "nullable": True}
        return schema

    def _get_parser(self):
        parser = super(OrdersService, self)._get_parser()
        parser += ["sale_channel", "suite_name"]
        return parser
