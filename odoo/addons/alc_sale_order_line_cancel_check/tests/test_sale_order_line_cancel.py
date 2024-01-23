# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.alc_sale_order_cancel.tests.common import TestSaleOrderCancelBase


class TestSaleOrderLineCancel(TestSaleOrderCancelBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wiz = cls.env["sale.order.line.cancel"].create({})
        cls.sol = cls.so.order_line

    def test_cancel_remaining_qty_started_picking(self):
        """Check printed picking can't be canceled."""
        self.pick.printed = True
        with self.assertRaises(UserError):
            self.wiz.with_context(
                active_id=self.sol.id, active_model=self.sol._name
            ).cancel_remaining_qty()

    def test_cancel_remaining_qty_done_preparation(self):
        """Check done picking can't be canceled."""
        self._do_transfer(self.pick)
        with self.assertRaises(UserError):
            self.wiz.with_context(
                active_id=self.sol.id, active_model=self.sol._name
            ).cancel_remaining_qty()
