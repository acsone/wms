# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel,
)


class StockLocation(Location):

    keep_track_of_release_channel = fields.Boolean()
    release_channel_id = fields.Many2one[StockReleaseChannel](
        string="Release channel", index=True
    )
