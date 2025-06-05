# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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

        matching_channels_ids = {
            c.id
            for c in self.env["stock.release.channel"].search(
                [("name", operator, value)]
            )
        }
        matching_partners_ids = []
        for partner in self.env["res.partner"].search([]):
            if any(
                channel.id in matching_channels_ids
                for channel in partner.located_in_stock_release_channel_ids
            ):
                matching_partners_ids.append(partner.id)

        return [("id", "in", matching_partners_ids)]
