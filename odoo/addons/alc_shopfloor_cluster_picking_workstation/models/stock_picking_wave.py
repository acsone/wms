# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    workstation_selected = fields.Boolean(
        default=False,
        help="Technical field set to True if the workstation has already been selected",
        compute="_compute_workstation_selected",
    )

    workstation_id = fields.Many2one("shopfloor.workstation")

    @api.depends("workstation_id")
    def _compute_workstation_selected(self):
        for rec in self:
            rec.workstation_selected = rec.workstation_id
