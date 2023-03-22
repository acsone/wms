# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

from .alc_stock_release_channel_tag import AlcStockReleaseChannelTag


class StockReleaseChannel(StockReleaseChannelBase):

    stock_release_channel_tag_ids = fields.Many2many[AlcStockReleaseChannelTag](
        string="Release channel tags"
    )
