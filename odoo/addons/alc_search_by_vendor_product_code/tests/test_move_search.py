# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import TestMoveLineSearchCommon


class TestMoveSearch(TestMoveLineSearchCommon):
    def test_move_search(self):
        StockMove = self.env["stock.move"]
        name_search_results = StockMove.name_search(self.product_code_base)
        self.assertTrue(name_search_results)
        moves = StockMove.browse(result[0] for result in name_search_results)
        self.assertTrue(
            any(move for move in moves if move.product_id == self.product_1)
        )
        self.assertTrue(
            any(move for move in moves if move.product_id == self.product_2)
        )
