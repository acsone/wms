# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_release_channel.models import stock_release_channel


class StockReleaseChannel(stock_release_channel.StockReleaseChannel):

    shape_name = fields.Char(
        help="Shape resource name into the imported shape file", readonly=True
    )
