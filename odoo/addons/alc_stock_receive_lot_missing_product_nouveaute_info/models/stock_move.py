# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):

    has_missing_info = fields.Boolean(
        default=False, compute="_compute_has_missing_info"
    )

    @api.depends("move_line_ids", "move_line_ids.has_missing_info")
    def _compute_has_missing_info(self):
        for move in self:
            move.has_missing_info = any(move.mapped("move_line_ids.has_missing_info"))
