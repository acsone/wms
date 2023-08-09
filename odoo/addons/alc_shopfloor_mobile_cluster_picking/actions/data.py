# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class DataAction(Component):
    _inherit = "shopfloor.data.action"

    @property
    def _picking_batch_parser(self):
        parser = super()._picking_batch_parser
        parser.append(("picking_device_id:device", lambda r, f: r[f].name or ""))
        parser.append(
            ("release_channel_ids:release_channels", self.release_channel_parser)
        )
        return parser

    @property
    def release_channel_parser(self):
        return ["channel_code:code", "display_name:name"]
