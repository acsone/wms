# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from odoo.addons.alc_sale_loyalty_year_end_rebate.tests.common import (
    TestSaleLoyaltyYearEndRebateCommon,
)


class TestSaleStockLoyalty(TestSaleLoyaltyYearEndRebateCommon):

    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        return res

    def _sell_product(self, product, qty):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.steve.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def _deliver_order(self, order, product, qty):
        picking = order.picking_ids.filtered(lambda p: p.state == "assigned")
        move_ids = picking.move_ids.filtered(
            lambda l: l.product_id == product and l.state not in ["cancel", "done"]
        )
        move_ids.write({"quantity_done": qty})
        picking._action_done()

    def _return_product(self, picking, product_qty):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return_wiz = stock_return_picking_form.save()
        return_wiz.product_return_moves.quantity = product_qty
        res = return_wiz.create_returns()
        return_pick = self.env["stock.picking"].browse(res["res_id"])
        # Validate picking
        return_pick.move_ids.write({"quantity_done": 2})
        return_pick._action_done()

    def test_accrual_points(self):
        self.assertTrue(self.year_end_rebate_program.is_nominative)
        order = self._sell_product(self.product_A, 10)
        sale_order_coupon_points = order.coupon_point_ids
        loyalty_cart = sale_order_coupon_points.coupon_id
        self.assertEqual(1, len(sale_order_coupon_points))
        self.assertEqual(0.0, sale_order_coupon_points.accrued_points)
        self.assertEqual(0.0, loyalty_cart.accrued_points)
        # deliver partially the order
        self._deliver_order(order, self.product_A, 5)
        self.assertEqual(5.0, order.order_line[0].qty_delivered)
        self.assertEqual(500, sale_order_coupon_points.accrued_points)

        # create a new order for the same customer
        order2 = self._sell_product(self.product_A, 10)
        sale_order_coupon_points2 = order2.coupon_point_ids
        loyalty_cart2 = sale_order_coupon_points2.coupon_id
        self.assertEqual(loyalty_cart, loyalty_cart2)
        # ont the seconde sale order coupon nothing should be accrued
        self.assertEqual(0.0, sale_order_coupon_points2.accrued_points)
        # We still have 500 points on the loyalty cart from the first order
        self.assertEqual(500, loyalty_cart.accrued_points)
        # deliver partially the second order
        self._deliver_order(order2, self.product_A, 5)
        self.assertEqual(5.0, order2.order_line[0].qty_delivered)
        self.assertEqual(500, sale_order_coupon_points2.accrued_points)

        # the total accrued points on the loyalty cart should be 1000 (500 + 500)
        self.assertEqual(1000, loyalty_cart.accrued_points)

        # if we deliver the remaining quantity of the first order
        self._deliver_order(order, self.product_A, 5)
        self.assertEqual(10.0, order.order_line[0].qty_delivered)
        self.assertEqual(1000, sale_order_coupon_points.accrued_points)
        # the total accrued points on the loyalty cart should be 1500 (1000 + 500)
        self.assertEqual(1500, loyalty_cart.accrued_points)

    def test_accrual_points_picking_return(self):
        order = self._sell_product(self.product_A, 10)
        sale_order_coupon_points = order.coupon_point_ids
        loyalty_cart = sale_order_coupon_points.coupon_id
        self.assertEqual(1, len(sale_order_coupon_points))
        self.assertEqual(0.0, sale_order_coupon_points.accrued_points)
        self.assertEqual(0.0, loyalty_cart.accrued_points)
        # deliver partially the order
        self._deliver_order(order, self.product_A, 7)
        self.assertEqual(7.0, order.order_line[0].qty_delivered)
        self.assertEqual(700, sale_order_coupon_points.accrued_points)

        # create a return picking for the delivered quantity
        picking = order.picking_ids.filtered(lambda p: p.state == "done")
        self._return_product(picking, 2)
        self.assertEqual(5.0, order.order_line[0].qty_delivered)
        self.assertEqual(500, sale_order_coupon_points.accrued_points)
        self.assertEqual(500, loyalty_cart.accrued_points)
