# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockMoveLineLockDone(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.assigned_picking = cls.env["stock.picking"].search(
            [("state", "=", "assigned")], limit=1
        )
        cls.move_line = cls.assigned_picking.move_line_ids[0]
        cls.package = cls.env["stock.quant.package"].create({"name": "PKG_OUT2"})

    def test_0(self):
        self.assertEqual(self.assigned_picking.state, "assigned")
        self.assigned_picking.action_set_quantities_to_reservation()
        self.assigned_picking._action_done()
        self.assertEqual(self.assigned_picking.state, "done")
        with self.assertRaises(UserError):
            self.move_line.package_id = self.package
        self.env.user.groups_id += self.env.ref(
            "stock_move_line_lock_qty_done.group_stock_move_can_edit_done_qty"
        )
        self.move_line.package_id = self.package
