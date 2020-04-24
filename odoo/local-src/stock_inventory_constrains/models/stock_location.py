# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_inventory_forbidden = fields.Boolean(
        string="Inventory on all products is forbidden",
        help="If set to True, you will not be able to generate an inventory on that location for 'all products'",
        default=False,
    )
