# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    shopfloor_packing_done = fields.Boolean(
        "Picking packed into shopfloor",
        help="If set, the picking has been put into a box by the shopfloor operator",
        compute="_compute_shopfloor_packing_done",
    )

    @api.depends("picking_ids", "picking_ids.shopfloor_packing_done")
    def _compute_shopfloor_packing_done(self):
        for rec in self:
            rec.shopfloor_packing_done = all(
                rec.picking_ids.mapped("shopfloor_packing_done")
            )
