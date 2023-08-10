# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_picking_batch.models.stock_picking_batch import (
    StockPickingBatch as StockPickingBatchBase,
)


class StockPickingBatch(StockPickingBatchBase):

    is_shopfloor_packing_todo = fields.Boolean(
        "Operations need to be packed",
        help="If set, some operations need to be packed by the shopdloor operator",
        compute="_compute_is_shopfloor_packing_todo",
    )

    @api.depends("picking_ids", "picking_ids.is_shopfloor_packing_todo")
    def _compute_is_shopfloor_packing_todo(self):
        for rec in self:
            rec.is_shopfloor_packing_todo = any(
                rec.picking_ids.mapped("is_shopfloor_packing_todo")
            )
