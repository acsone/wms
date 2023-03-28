# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    release_channel_can_allow_pick = fields.Boolean(
        string="User can allow picking preparation on release channels?",
        help="If true, users can allow/disallow picking preparation for this type on "
        "release channels",
    )
