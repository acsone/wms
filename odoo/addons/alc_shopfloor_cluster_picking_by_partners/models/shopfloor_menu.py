# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.shopfloor_batch_automatic_creation.models.shopfloor_menu import (
    ShopfloorMenu as ShopfloorMenuBase,
)


class ShopfloorMenu(ShopfloorMenuBase):

    group_pickings_by_partner = fields.Boolean(
        default=False,
        string="Group pickings by partner",
        help="If set to true, all the pickings related to one partner will be put in one bin",
    )
