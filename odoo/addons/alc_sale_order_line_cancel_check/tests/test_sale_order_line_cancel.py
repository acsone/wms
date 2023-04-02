# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.sale_order_line_cancel.tests.common import TestSaleOrderLineCancelBase


class TestSaleOrderLineCancel(TestSaleOrderLineCancelBase):
    def test_cancel_remaining_qty_started_picking(self):
        """Check printed picking can't be canceled."""
        ship = self.sale.picking_ids
        ship.printed = True
        with self.assertRaises(UserError):
            self.wiz.with_context(
                active_id=self.sale.order_line.id
            ).cancel_remaining_qty()
