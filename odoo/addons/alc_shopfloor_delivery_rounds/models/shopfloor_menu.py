# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopfloorMenu(models.Model):

    _inherit = "shopfloor.menu"

    only_one_delivery_round_by_cluster = fields.Boolean(
        string="Create cluster pickings by delivery rounds", default=True,
    )
