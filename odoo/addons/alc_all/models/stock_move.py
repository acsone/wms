# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import index_exists

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    def init(self):
        """
        This index improves the overall performance of picking validation.

        A flush_all in _update_reserved_quantity makes the computed fields recomputed
        with each stock.move action_done.
        """
        if not index_exists(self._cr, "stock_quant_location_id_product_id_manidx"):
            self._cr.execute(
                """
                CREATE INDEX stock_move_move_rel_move_dest_id_manidx
                ON
                    stock_move_move_rel (move_dest_id)
                """
            )
