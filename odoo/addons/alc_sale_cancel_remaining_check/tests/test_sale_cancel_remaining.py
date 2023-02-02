# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.sale_cancel_remaining.tests.common import TestSaleCancelRemainingBase


class TestSaleCancelRemaining(TestSaleCancelRemainingBase):
    def test_cancel_remaining_qty_started_picking(self):
        """Check printed picking can't be canceled."""
        pick = self.sale.picking_ids.filtered(
            lambda picking: picking.picking_type_code == "internal"
            and picking.state not in ("cancel", "done")
        )
        pick.printed = True
        with self.assertRaises(UserError):
            self.wiz.with_context(
                active_id=self.sale.order_line.id
            ).cancel_remaining_qty()
