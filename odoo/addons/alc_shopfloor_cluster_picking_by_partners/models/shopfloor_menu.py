# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopfloorMenu(models.Model):

    _inherit = "shopfloor.menu"
    group_pickings_by_partner = fields.Boolean(
        default=False,
        string="Group pickings by partner",
        help="If set to true, all the pickings related to one partner will be put in one bin",
    )
