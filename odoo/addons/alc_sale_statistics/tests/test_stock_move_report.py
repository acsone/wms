# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from .common import TestStockMoveReportCommon


class TestStockMoveReport(TestStockMoveReportCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_stock_move_report_full(self):
        # statistics on a period containing all stock moves
        smr_lines = self._get_stock_move_report_lines(
            self.today - timedelta(days=10), self.today
        )
        self.assertEqual(len(smr_lines), 4)
        # check 'smr partner 1': 1 move out +5 (J-1) and 1 move in -2 (J)
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 1")
        self.assertEqual(len(moves), 2)
        self.assertEqual(moves[0].partner_invoice_zip_prov, "4000")
        self.assertEqual(moves[0].product_name, "smr product 1")
        self.assertEqual(moves[0].product_qty, -2)
        self.assertEqual(moves[0].validation_date, self.today)
        self.assertEqual(moves[0].product_name, "smr product 1")
        self.assertEqual(moves[1].product_qty, 5)
        self.assertEqual(moves[1].validation_date, self.today - timedelta(days=1))
        # check 'smr partner 2': 1 move out +6 (J-2)
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 2")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].partner_invoice_zip_prov, "6000")
        self.assertEqual(moves[0].product_name, "smr product 2")
        self.assertEqual(moves[0].product_qty, 6)
        self.assertEqual(moves[0].validation_date, self.today - timedelta(days=2))
        # check 'smr partner 3': 1 move out +7 (J-3)
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 3")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].partner_invoice_zip_prov, "6600")
        self.assertEqual(moves[0].product_name, "smr product 3")
        self.assertEqual(moves[0].product_qty, 7)
        self.assertEqual(moves[0].validation_date, self.today - timedelta(days=3))
        # check 'smr supplier 1': 2 moves out +5 (J-1) and +7 (j-3) and 1 move in -2 (J)
        moves = smr_lines.filtered(lambda x: x.supplier_name == "smr supplier 1")
        self.assertEqual(len(moves), 3)
        self.assertEqual(moves[0].product_name, "smr product 1")
        self.assertEqual(moves[0].product_qty, -2)
        self.assertEqual(moves[0].validation_date, self.today)
        self.assertEqual(moves[1].product_name, "smr product 1")
        self.assertEqual(moves[1].product_qty, 5)
        self.assertEqual(moves[1].validation_date, self.today - timedelta(days=1))
        self.assertEqual(moves[2].product_name, "smr product 3")
        self.assertEqual(moves[2].product_qty, 7)
        self.assertEqual(moves[2].validation_date, self.today - timedelta(days=3))
        # check 'smr supplier 2': 1 move out +6 (J-2)
        moves = smr_lines.filtered(lambda x: x.supplier_name == "smr supplier 2")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].product_name, "smr product 2")
        self.assertEqual(moves[0].product_qty, 6)
        self.assertEqual(moves[0].validation_date, self.today - timedelta(days=2))

    def test_stock_move_report_small_period(self):
        # statistics on a period containing one stock move
        smr_lines = self._get_stock_move_report_lines(
            self.today - timedelta(days=10), self.today - timedelta(days=3)
        )
        self.assertEqual(len(smr_lines), 1)
        # check 'smr partner 1': 0 move
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 1")
        self.assertEqual(len(moves), 0)
        # check 'smr partner 2': 0 move
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 2")
        self.assertEqual(len(moves), 0)
        # check 'smr partner 3': 1 move out +7 (J-3)
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 3")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].product_name, "smr product 3")
        self.assertEqual(moves[0].product_qty, 7)
        self.assertEqual(moves[0].validation_date, self.today - timedelta(days=3))
        # check 'smr supplier 1': 1 moves out +7 (j-3)
        moves = smr_lines.filtered(lambda x: x.supplier_name == "smr supplier 1")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].product_name, "smr product 3")
        self.assertEqual(moves[0].product_qty, 7)
        self.assertEqual(moves[0].validation_date, self.today - timedelta(days=3))
        # check 'smr supplier 2': 0 move
        moves = smr_lines.filtered(lambda x: x.supplier_name == "smr supplier 2")
        self.assertEqual(len(moves), 0)

    def test_stock_move_report_only_one_supplier(self):
        # statistics on a period containing all stock moves but only 'smr supplier 2'
        # wants statistics
        self.supplier[0].ask_sale_statistics = False
        self.supplier.flush_recordset()
        smr_lines = self._get_stock_move_report_lines(
            self.today - timedelta(days=10), self.today
        )
        self.assertEqual(len(smr_lines), 1)
        # check 'smr partner 1': 0 move
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 1")
        self.assertEqual(len(moves), 0)
        # check 'smr partner 2': 1 move out +6 (J-2)
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 2")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].product_name, "smr product 2")
        self.assertEqual(moves[0].product_qty, 6)
        self.assertEqual(moves[0].validation_date, self.today - timedelta(days=2))
        # check 'smr partner 3': 0 move
        moves = smr_lines.filtered(lambda x: x.partner_invoice_name == "smr partner 3")
        self.assertEqual(len(moves), 0)
        # check 'smr supplier 1': 0 move
        moves = smr_lines.filtered(lambda x: x.supplier_name == "smr supplier 1")
        self.assertEqual(len(moves), 0)
        # check 'smr supplier 2': 1 moves out +6 (j-2)
        moves = smr_lines.filtered(lambda x: x.supplier_name == "smr supplier 2")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].product_name, "smr product 2")
        self.assertEqual(moves[0].product_qty, 6)
        self.assertEqual(moves[0].validation_date, self.today - timedelta(days=2))
