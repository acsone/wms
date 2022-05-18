# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    delivery_round_ids = fields.Many2many(
        comodel_name="round.instance",
        compute="_compute_delivery_round_ids",
        string="Delivery Round(s)",
        store=True,
        readonly=True,
        track_visibility="onchange",
        index=True,
    )

    @api.depends("picking_ids", "picking_ids.delivery_round_id")
    def _compute_delivery_round_ids(self):
        for rec in self:
            rec.delivery_round_ids = rec.picking_ids.mapped("delivery_round_id")
