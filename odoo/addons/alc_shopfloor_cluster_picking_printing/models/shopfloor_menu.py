# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopfloorMenu(models.Model):
    _inherit = "shopfloor.menu"

    print_on_pack_pickings = fields.Boolean(
        string="Print Labels on Pack Pickings",
        default=False,
        help="When ticked, pack and product labels are printed as result of "
        "the put in pack action.",
    )
