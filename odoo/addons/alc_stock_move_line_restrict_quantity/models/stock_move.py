# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    def _do_unreserve(self):
        new_self = self.with_context(no_restriction_quantity_ids=self.move_line_ids.ids)
        return super(StockMove, new_self)._do_unreserve()
