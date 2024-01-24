# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import TestSaleOrderCancelBase


class TestSaleOrderCancel(TestSaleOrderCancelBase):
    def test_1(self):
        self.assertEqual(len(self.so.picking_ids), 2)
        self._do_transfer(self.pick)
        self.assertEqual(self.pick.state, "done")
        with self.assertRaises(UserError):
            self.so.action_cancel()
