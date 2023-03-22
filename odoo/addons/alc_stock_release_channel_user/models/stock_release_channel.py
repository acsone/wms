# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_users import Users
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):

    user_ids = fields.Many2many[Users](
        string="Users",
        copy=False,
        help="Users assigned to this channel. Fill this list to restrict the "
        "processing of the pickings to specific list of users. Leaves"
        "empty to allows the processing by any user.",
    )
