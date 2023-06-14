# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):
    @api.model
    def assign_release_channel(self, picking):
        picking.ensure_one()
        if (
            not picking.ignore_release_channel_block
            and picking.is_backorder_due_to_unavailability
        ):
            return None
        return super().assign_release_channel(picking)
