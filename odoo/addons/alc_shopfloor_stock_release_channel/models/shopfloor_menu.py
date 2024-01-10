# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor_base.models.shopfloor_menu import (
    ShopfloorMenu as ShopfloorMenuBase,
)


class ShopfloorMenu(ShopfloorMenuBase):

    release_channel_required = fields.Boolean(
        string="Only pickings in a release channel",
        help="Only the pickings assigned to a release channel will be selected for this batch.",
        default=False,
    )
