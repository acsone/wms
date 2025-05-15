# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):

    # the default order uses result_packaging_id, which make all queries join the table
    # to get the package name to sort with
    _order = "id"

    def init(self):
        # this index improves the queries on location_dest_id ordered by id
        self._cr.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_location_dest_id_id
            ON stock_move_line(location_dest_id, id);
            """
        )
