# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.sale_order_line_cancel.tests.common import TestSaleOrderLineCancelBase


class TestSaleCancelRemaining(TestSaleOrderLineCancelBase):
    def test_deliver_and_return_order(self):
        order_line = self.sale.order_line
        ship = order_line.move_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        pick = ship.move_orig_ids
        pick._action_assign()
        pick.quantity_done = 9
        pick._action_done()
        ship._action_assign()
        ship.quantity_done = 9
        self.assertEqual(order_line.product_qty_remains_to_deliver, 10)
        ship._action_done()
        self.assertEqual(order_line.qty_delivered, 9)
        self.assertEqual(order_line.product_qty_remains_to_deliver, 1)

        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=ship.picking_id.ids,
                active_id=ship.picking_id.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = 2.0  # Return only 2
        action = stock_return_picking.create_returns()
        return_pick = self.env["stock.picking"].browse(action["res_id"])
        return_pick.move_ids.quantity_done = 2.0
        return_pick._action_done()

    def test_returned_qty(self):
        self.test_deliver_and_return_order()
        self.assertEqual(self.sale.order_line.qty_delivered, 7)
        self.assertEqual(self.sale.order_line.product_qty_returned, 2)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 1)
        wiz = self.env["sale.order.line.cancel"].create({})
        wiz.with_context(
            active_id=self.sale.order_line.id, active_model=self.sale.order_line._name
        ).cancel_remaining_qty()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 1)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)

    def test_returned_qty_for_cost_expense_product(self):
        self.sale.order_line.product_id.expense_policy = "cost"
        self.test_deliver_and_return_order()
        self.assertEqual(self.sale.order_line.qty_delivered, 7)
        self.assertEqual(self.sale.order_line.product_qty_returned, 0)
