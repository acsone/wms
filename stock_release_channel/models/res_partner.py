# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    stock_release_channel_ids = fields.Many2many(
        comodel_name="stock.release.channel",
        string="Release Channels",
        help="You can choose a dedicated release channel for this partner. All of their"
        " transfers will be assigned to the selected channel, regardless of the "
        "automatic assigning process.",
    )

    def _get_partner_release_channel(self):
        if not self:
            return None
        release_channels = self.stock_release_channel_ids.filtered(
            lambda r: r.active and r.state != "asleep"
        )
        if not release_channels:
            return None
        if len(release_channels) == 1:
            return release_channels
        return release_channels.sorted("sequence")[0]
