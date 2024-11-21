# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tools import drop_index, index_exists

from odoo.addons.stock.models.stock_lot import StockLot
from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):

    lot_id = fields.Many2one[StockLot](index="btree_not_null")

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "stock_move_line_result_package_id_index",
        ):
            # covered by the previous index
            drop_index(
                self._cr, "stock_move_line_result_package_id_manidx", "stock_move_line"
            )
