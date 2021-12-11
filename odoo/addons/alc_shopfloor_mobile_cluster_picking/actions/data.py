# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class DataAction(Component):
    _inherit = "shopfloor.data.action"

    @property
    def _picking_batch_parser(self):
        parser = super(DataAction, self)._picking_batch_parser
        parser.append(("picking_device_id:device", lambda r, f: r[f].name or ""))
        parser.append(("delivery_round_id:delivery_round", self.delivery_round_parser))
        return parser

    @property
    def delivery_round_parser(self):
        return ["template_code:code", "display_name:name"]
