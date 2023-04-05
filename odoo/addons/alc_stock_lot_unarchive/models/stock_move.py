# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    def _action_done(self, cancel_backorder=False):
        """When stock movement are done, unarchive corresponding lots."""
        res = super()._action_done(cancel_backorder=cancel_backorder)
        lots = self.filtered("lot_ids.is_archived").mapped("lot_ids")
        lots.write({"is_archived": False})
        return res
