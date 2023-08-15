# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor_base.models.shopfloor_menu import (
    ShopfloorMenu as ShopfloorMenuBase,
)


class ShopfloorMenu(ShopfloorMenuBase):

    scan_workstation = fields.Boolean(
        string="Scan workstation during scenario",
        default=False,
        help="If you tick this box, you will have to scan the workstation"
        " before starting the put in pack.",
    )
