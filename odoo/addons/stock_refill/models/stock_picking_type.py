# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    ignore_putaway_reserve = fields.Boolean(
        help="Ignore putaway location when computing the putaway location",
        default=False,
    )
