# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor_base.models.shopfloor_menu import (
    ShopfloorMenu as ShopfloorMenuBase,
)


class ShopfloorMenu(ShopfloorMenuBase):

    restrict_to_same_release_channel = fields.Boolean(
        string="Restrict to the same release channel",
        help="Only the pickings with the same release channel will be selected for this batch.",
        default=False,
    )
