# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        move_done = self.filtered(lambda r: r.state == "done").sudo()
        move_done.rma_receiver_ids._create_inventory_activity_reception()
        move_done.rma_id._create_inventory_activity_delivery()
        return res
