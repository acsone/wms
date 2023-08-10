# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor_base.models.shopfloor_menu import (
    ShopfloorMenu as ShopfloorMenuBase,
)


class ShopfloorMenu(ShopfloorMenuBase):

    pack_pickings = fields.Boolean(
        string="Pack pickings",
        default=False,
        help="If you tick this box, all the picked item will be put in pack"
        " before the transfer.",
    )
