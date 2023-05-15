# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel_propagate_channel_picking.models.stock_release_channel import (
    StockReleaseChannel as ReleaseChannelBase,
)


class StockReleaseChannel(ReleaseChannelBase):

    propagate_to_pickings_chain = fields.Boolean(default=True)
