# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class DataAction(Component):
    _inherit = "shopfloor.data.action"

    @property
    def _picking_parser(self):
        parser = super()._picking_parser
        parser.append(
            ("release_channel_id:release_channel", self.release_channel_parser)
        )
        return parser

    @property
    def release_channel_parser(self):
        return ["channel_code:code", "display_name:name"]
