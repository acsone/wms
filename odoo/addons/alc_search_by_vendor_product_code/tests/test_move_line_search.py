# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import TestMoveLineSearchCommon


class TestMoveLineSearch(TestMoveLineSearchCommon):
    def test_move_line_search(self):
        StockMoveLine = self.env["stock.move.line"]
        name_search_results = StockMoveLine.name_search(self.product_code_base)
        self.assertTrue(name_search_results)
        move_lines = StockMoveLine.browse(result[0] for result in name_search_results)
        self.assertTrue(
            any(
                move_line
                for move_line in move_lines
                if move_line.product_id == self.product_1
            )
        )
        self.assertTrue(
            any(
                move_line
                for move_line in move_lines
                if move_line.product_id == self.product_2
            )
        )
