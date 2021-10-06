# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    wave_volume_liter = fields.Float(
        string="Volume (l)",
        help="Indicates total volume of transfers included.",
        compute="_compute_wave_volume_liter",
    )

    @api.depends("wave_volume")
    def _compute_wave_volume_liter(self):
        for rec in self:
            rec.wave_volume_liter = rec.wave_volume * 1000.0
