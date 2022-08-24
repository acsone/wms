# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    picking_type_id = fields.Many2one(
        comodel="stock.picking.type", store=True, related="picking_ids.picking_type_id"
    )
