# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as ReleaseChannel,
)


class StockReleaseChannel(ReleaseChannel):

    channel_code = fields.Char(
        string="Code",
        required=True,
        default="0",
        help="Replacement for old round template code",
    )
