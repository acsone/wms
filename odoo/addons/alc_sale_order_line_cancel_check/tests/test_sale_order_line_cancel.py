# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import TestSaleOrderCancelBase


class TestSaleOrderLineCancel(TestSaleOrderCancelBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wiz = cls.env["sale.order.line.cancel"].create({})
        cls.sol = cls.so.order_line

    def _cancel_remaining_qty(self):
        self.wiz.with_context(
            active_id=self.sol.id, active_model=self.sol._name
        ).cancel_remaining_qty()

    def test_cancel_remaining_qty_started_picking(self):
        """Check printed picking can't be canceled."""
        self.pick.printed = True
        with self.assertRaises(UserError):
            self._cancel_remaining_qty()

    def test_cancel_remaining_qty_done_preparation(self):
        """Check done picking can't be canceled."""
        self._do_transfer(self.pick)
        with self.assertRaises(UserError):
            self._cancel_remaining_qty()

    def test_cancel_remaining_qty_partially_done_preparation(self):
        self.pick.printed = True
        self.pick.move_line_ids.qty_done = 2
        with self.assertRaises(UserError):
            # if the pick is started, we don't allow line cancel
            self._cancel_remaining_qty()
        self.pick._action_done()
        with self.assertRaises(UserError):
            # if the preparation is done but the out is not done yet
            # we don't allow line cancel
            self._cancel_remaining_qty()
        self.pick.printed = False
        with self.assertRaises(UserError):
            # even if the pick was done manually, and not printed
            # we don't allow the cancel
            self._cancel_remaining_qty()
        self.out.move_line_ids.qty_done = 2
        self.out._action_done()
        self.assertEqual(self.sol.qty_delivered, 2)
        self.assertEqual(self.sol.product_qty_remains_to_deliver, 3)
        # no the out is done, we allow the cancel of the remaining qties
        self._cancel_remaining_qty()
        self.assertEqual(self.sol.product_qty_canceled, 3)
        self.assertEqual(self.sol.product_qty_remains_to_deliver, 0)
