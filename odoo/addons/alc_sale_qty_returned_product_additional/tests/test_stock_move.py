# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form

from odoo.addons.alc_additional_product_stock.tests.common import StockPickingTestCase


class TestStockMove(StockPickingTestCase):
    def test_00(self):
        sale = self._confirm_sale_order(products=[self.main_product], qty=10)
        pick = self._get_picking_pick(sale)
        ship = self._get_picking_ship(sale)
        self.assertIn(self.additional_product, pick.mapped("move_ids.product_id"))
        self.assertIn(self.additional_product, ship.mapped("move_ids.product_id"))
        pick.action_confirm()
        pick.action_assign()
        # In the interface, you cannot modify cancelled moves
        for move in pick.move_ids.filtered(lambda move: move.state != "cancel"):
            move.quantity_done = move.product_qty
        pick._action_done()
        ship.action_confirm()
        ship.action_assign()
        for move in ship.move_ids.filtered(lambda move: move.state != "cancel"):
            move.quantity_done = move.product_qty
        ship._action_done()

        # Make sure additional product is in the loop

        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=ship.ids, active_id=ship.id, active_model="stock.picking"
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.write({"quantity": 10})
        action = stock_return_picking.create_returns()
        return_pick = self.env["stock.picking"].browse(action["res_id"])
        return_pick.move_ids.write({"quantity_done": 10})
        return_pick._action_done()

        # Make sure only the 10 items from the main product are returned
        main_sol = sale.order_line.filtered(lambda l: l.product_id == self.main_product)
        additional_sol = sale.order_line - main_sol
        self.assertEqual(main_sol.product_qty_returned, 10.0)
        self.assertEqual(additional_sol.qty_delivered, 40.0)
        self.assertEqual(additional_sol.product_qty_returned, 0.0)
