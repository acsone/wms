# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    total_volume_batch_picking_liter = fields.Float(
        string="Volume (l)",
        help="Indicates total volume of transfers included.",
        compute="_compute_total_volume_batch_picking_liter",
    )

    @api.depends("total_volume_batch_picking")
    def _compute_total_volume_batch_picking_liter(self):
        for rec in self:
            rec.total_volume_batch_picking_liter = (
                rec.total_volume_batch_picking * 1000.0
            )
