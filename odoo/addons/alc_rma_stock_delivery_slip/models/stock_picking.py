# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_delivery_slip.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):

    def _delivery_slip_moves(self, is_entry_register):
        moves = super()._delivery_slip_moves(is_entry_register)
        if self.env.context.get("csv_note"):
            moves = moves - moves.filtered(
                lambda m: m.rma_id.operation_id.no_csv_delivery_slip
            )
        return moves

    def get_entry_register_lines(self):
        if any(
            self.move_ids.rma_receiver_ids.operation_id.mapped(
                "no_entry_register_at_reception"
            )
        ):
            return self.env["stock.move"]
        moves = super().get_entry_register_lines()
        moves = moves - moves.filtered(
            lambda m: m.rma_id.operation_id.no_entry_register_at_delivery
        )
        return moves
