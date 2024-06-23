# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.sale_order_line_cancel.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):
    @api.model
    def _get_moves_to_cancel(self):
        moves_to_cancel = super()._get_moves_to_cancel()
        # extend to move_orig_ids
        moves_to_cancel |= moves_to_cancel.mapped("move_orig_ids").filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        return moves_to_cancel

    def _is_cancel_sales_bo_gt_3months_allowed(self):
        self.ensure_one()
        moves = self.move_ids
        remaining_moves = moves.filtered(lambda m: m.state not in ("cancel", "done"))
        if not remaining_moves:
            return False
        if True in remaining_moves.mapped("picking_id.printed"):
            return False
        internal_moves = remaining_moves.move_orig_ids
        if "done" in internal_moves.mapped("state"):
            return False
        if True in internal_moves.mapped("picking_id.printed"):
            return False
        return self.order_id.auto_finalize_processing
