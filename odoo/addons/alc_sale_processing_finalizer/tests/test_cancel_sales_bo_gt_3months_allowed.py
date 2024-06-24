# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSaleProcessingFinalizerComon


class TestCancelSalesBoGt3monthsAllowed(TestSaleProcessingFinalizerComon):
    """
    Test sale order line cancellation at sale order finalization.

    A sales order line can be automatically canceled after 3 months if it has not been
    processed, provided it meets the following criteria:
        - The order is set to auto_finalize_processing.
        - The related move is neither completed nor printed.
        - The preparation move is neither completed nor printed.
    Special case:
        If the preparation move was removed, the cancellation is still allowed if the
        above criteria are met.
    """

    def test_1(self):
        """The order is set to auto_finalize_processing."""
        sol = self.so_auto_finalize.order_line
        self.assertTrue(sol._is_cancel_sales_bo_gt_3months_allowed())
        self.so_auto_finalize.auto_finalize_processing = False
        self.assertFalse(sol._is_cancel_sales_bo_gt_3months_allowed())

    def test_2(self):
        """The related move is neither completed nor printed."""
        sol = self.so_auto_finalize.order_line
        self.assertTrue(sol._is_cancel_sales_bo_gt_3months_allowed())
        sol.move_ids.picking_id.printed = True
        self.assertFalse(sol._is_cancel_sales_bo_gt_3months_allowed())

    def test_3(self):
        """The preparation move is neither completed nor printed."""
        sol = self.so_auto_finalize.order_line
        self.assertTrue(sol._is_cancel_sales_bo_gt_3months_allowed())
        internal_move = sol.move_ids.move_orig_ids
        internal_move.picking_id.printed = True
        self.assertFalse(sol._is_cancel_sales_bo_gt_3months_allowed())
        internal_move.picking_id.printed = False
        self.assertTrue(sol._is_cancel_sales_bo_gt_3months_allowed())
        internal_move.picking_id.action_set_quantities_to_reservation()
        internal_move.picking_id._action_done()
        self.assertFalse(sol._is_cancel_sales_bo_gt_3months_allowed())

    def test_4(self):
        """If the preparation move was removed, the cancellation is still allowed."""
        sol = self.so_auto_finalize.order_line
        self.assertTrue(sol._is_cancel_sales_bo_gt_3months_allowed())
        internal_move = sol.move_ids.move_orig_ids
        internal_move._action_cancel()
        internal_move.unlink()
        self.assertFalse(internal_move.exists())
        self.assertTrue(sol._is_cancel_sales_bo_gt_3months_allowed())
