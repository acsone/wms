# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    shopfloor_packing_done = fields.Boolean(
        "Picking packed into shopfloor",
        help="If set, the picking has been put into a box by the shopfloor operator",
        default=False,
    )
