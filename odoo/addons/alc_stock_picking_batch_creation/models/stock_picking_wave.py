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

    def confirm_picking(self):
        """
        Context key added to hack the action_assign on the pickings in the case of a wave picking to be validated
        (because in the case of Alcyon, pickings are already assigned)
        """
        return super(
            StockPickingWave, self.with_context(from_cluster_confirm=True)
        ).confirm_picking()
