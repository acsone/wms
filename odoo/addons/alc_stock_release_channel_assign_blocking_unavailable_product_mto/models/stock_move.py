# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):

    def _get_stock_release_channel_block_on_backorder(self):
        """
        Get the condition to block further delivery on backorder.

        Here, don't block if generated move has used an MTO route
        """
        self.ensure_one()
        if self.rule_id.route_id.is_mto:
            return False
        return super()._get_stock_release_channel_block_on_backorder()
