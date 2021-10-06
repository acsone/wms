# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    delivery_round_id = fields.Many2one(
        related="picking_ids.delivery_round_id",
        string="Delivery Round",
        store=True,
        readonly=True,
        track_visibility="onchange",
        index=True,
    )
