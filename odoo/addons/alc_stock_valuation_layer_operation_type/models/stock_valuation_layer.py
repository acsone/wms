# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock.models.stock_picking import PickingType
from odoo.addons.stock_account.models.stock_valuation_layer import (
    StockValuationLayer as StockValuationLayerBase,
)


class StockValuationLayer(StockValuationLayerBase):

    picking_type_id = fields.Many2one[PickingType](
        related="stock_move_id.picking_type_id",
        store=True,
        index=True,
        string="Picking Type",
    )
    picking_type_code = fields.Selection(
        related="picking_type_id.code", store=True, index=True, string="Operation Type"
    )
    operation_direction = fields.Selection(
        selection=[
            ("in", "In"),
            ("out", "Out"),
        ],
        compute="_compute_operation_direction",
        store=True,
        index=True,
    )

    @api.depends("quantity")
    def _compute_operation_direction(self):
        for rec in self:
            operation_direction = False
            if rec.quantity > 0:
                operation_direction = "in"
            elif rec.quantity < 0:
                operation_direction = "out"
            rec.operation_direction = operation_direction
