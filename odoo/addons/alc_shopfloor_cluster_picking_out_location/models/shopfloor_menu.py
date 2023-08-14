# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor.models.shopfloor_menu import (
    ShopfloorMenu as ShopfloorMenuBase,
)


class ShopfloorMenu(ShopfloorMenuBase):

    _inherit = "shopfloor.menu"
    unload_on_specific_location = fields.Boolean(
        string="Unload packs in specific OUT locations",
        default=False,
        help="If you tick this box, you will have to unload"
        " your packs into specific out locations.",
    )
