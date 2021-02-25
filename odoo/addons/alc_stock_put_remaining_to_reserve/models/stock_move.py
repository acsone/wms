# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    picking_reserve_id = fields.Many2one(
        "stock.picking",
        "Picking To reserve of",
        related="picking_id.picking_reserve_id",
        index=True,
    )
