# Copyright 2024 ASCONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock.models.stock_lot import StockLot as StockLotBase


class StockLot(StockLotBase):
    is_empty = fields.Boolean(
        string="Is Empty?", compute="_compute_is_empty", store=True, index=True
    )

    @api.depends("quant_ids")
    def _compute_is_empty(self):
        for rec in self:
            internal_quants = rec.quant_ids.filtered(
                lambda q: q.location_id.usage == "internal"
            )

            if not internal_quants:
                rec.is_empty = True
            else:
                rec.is_empty = all(quant.quantity == 0 for quant in internal_quants)
