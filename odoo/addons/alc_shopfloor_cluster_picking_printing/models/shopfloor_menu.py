# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor_base.models.shopfloor_menu import (
    ShopfloorMenu as ShopfloorMenuBase,
)


class ShopfloorMenu(ShopfloorMenuBase):

    print_on_pack_pickings = fields.Boolean(
        string="Print Labels on Pack Pickings",
        default=False,
        help="When ticked, pack and product labels are printed as result of "
        "the put in pack action.",
    )
