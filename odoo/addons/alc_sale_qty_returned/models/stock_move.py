# Copyright 2019 Camptocamp S.A.
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_stock.models.stock import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    def _action_done(self, cancel_backorder=False):
        result = super()._action_done(cancel_backorder=cancel_backorder)
        for move in self:
            if not move.origin_returned_move_id:
                continue
            line = move.sale_line_id
            if not move._include_move_into_return_quantity() or move.scrapped:
                continue
            if move.location_dest_id.usage != "customer":
                line.product_qty_returned += move.product_uom_qty
            else:
                line.product_qty_returned -= move.product_uom_qty
        return result

    def _include_move_into_return_quantity(self):
        self.ensure_one()
        line = self.sale_line_id
        if self.product_id.expense_policy != "no" or not line:
            return False
        return True
