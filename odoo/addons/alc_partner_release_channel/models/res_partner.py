# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from shapely.ops import unary_union

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    located_in_stock_release_channel_ids = fields.Many2many(
        search="_search_located_in_stock_release_channel_ids"
    )

    @api.model
    def _search_located_in_stock_release_channel_ids(self, operator, value):
        if operator not in ("like", "ilike") or not isinstance(value, str):
            raise UserError(_("Operation not supported"))

        matching_channels_zones_union = unary_union(
            [
                rc.delivery_zone
                for rc in self.env["stock.release.channel"].search(
                    [("name", operator, value)]
                )
                if rc.delivery_zone
            ]
        )
        return [("geo_point", "geo_within", matching_channels_zones_union)]
