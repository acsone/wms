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
        programs = cls.env["loyalty.program"].search(
            [("id", "!=", cls.year_end_rebate_program.id)]
        )
        programs.write({"active": False})
        cls.year_end_rebate_program.rule_ids.reward_point_max_amount = 10
        cls.steve_bis = cls.steve.copy({"name": "Steve Bis"})
        cls.so_with_loyalty = cls.env["sale.order"].create(
            {
                "partner_id": cls.steve_bis.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_A.id,
                            "product_uom_qty": 10,
                        },
                    )
                ],
            }
        )
        cls.so_with_loyalty.action_confirm()
        cls._deliver_order(cls.so_with_loyalty, cls.product_A, 10)
        return res

    @classmethod
    def _sell_product(cls, product, qty, partner=None):
        partner = partner or cls.env["res.partner"].browse()
        order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id or cls.steve.id,
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

    @classmethod
    def _deliver_order(cls, order, product, qty):
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
        self.assertEqual(0.0, loyalty_cart.max_accrued_points)
        self.assertEqual(0.0, loyalty_cart.accrued_points)
        self.assertEqual(0.0, loyalty_cart.max_accrued_points)
        # deliver partially the order
        self._deliver_order(order, self.product_A, 5)
        self.assertEqual(5.0, order.order_line[0].qty_delivered)
        self.assertEqual(500, sale_order_coupon_points.accrued_points)
        self.assertEqual(500, loyalty_cart.accrued_points)
        self.assertEqual(5000, sale_order_coupon_points.max_accrued_points)
        self.assertEqual(5000, loyalty_cart.max_accrued_points)

        # create a new order for the same customer
        order2 = self._sell_product(self.product_A, 10)
        sale_order_coupon_points2 = order2.coupon_point_ids
        loyalty_cart2 = sale_order_coupon_points2.coupon_id
        self.assertEqual(loyalty_cart, loyalty_cart2)
        # ont the seconde sale order coupon nothing should be accrued
        self.assertEqual(0.0, sale_order_coupon_points2.accrued_points)
        self.assertEqual(0.0, sale_order_coupon_points2.max_accrued_points)
        # We still have 500 points on the loyalty cart from the first order
        self.assertEqual(500, loyalty_cart.accrued_points)
        # deliver partially the second order
        self._deliver_order(order2, self.product_A, 5)
        self.assertEqual(5.0, order2.order_line[0].qty_delivered)
        self.assertEqual(500, sale_order_coupon_points2.accrued_points)
        self.assertEqual(5000, sale_order_coupon_points2.max_accrued_points)

        # the total accrued points on the loyalty cart should be 1000 (500 + 500)
        self.assertEqual(1000, loyalty_cart.accrued_points)
        self.assertEqual(10000, loyalty_cart.max_accrued_points)

        # if we deliver the remaining quantity of the first order
        self._deliver_order(order, self.product_A, 5)
        self.assertEqual(10.0, order.order_line[0].qty_delivered)
        self.assertEqual(1000, sale_order_coupon_points.accrued_points)
        # the total accrued points on the loyalty cart should be 1500 (1000 + 500)
        self.assertEqual(1500, loyalty_cart.accrued_points)
        self.assertEqual(15000, loyalty_cart.max_accrued_points)

    def test_accrual_points_picking_return(self):
        order = self._sell_product(self.product_A, 10)
        sale_order_coupon_points = order.coupon_point_ids
        loyalty_cart = sale_order_coupon_points.coupon_id
        self.assertEqual(1, len(sale_order_coupon_points))
        self.assertEqual(0.0, sale_order_coupon_points.accrued_points)
        self.assertEqual(0.0, loyalty_cart.accrued_points)
        self.assertEqual(0.0, loyalty_cart.max_accrued_points)
        # deliver partially the order
        self._deliver_order(order, self.product_A, 7)
        self.assertEqual(7.0, order.order_line[0].qty_delivered)
        self.assertEqual(700, sale_order_coupon_points.accrued_points)
        self.assertEqual(7000, sale_order_coupon_points.max_accrued_points)

        # create a return picking for the delivered quantity
        picking = order.picking_ids.filtered(lambda p: p.state == "done")
        self._return_product(picking, 2)
        self.assertEqual(5.0, order.order_line[0].qty_delivered)
        self.assertEqual(500, sale_order_coupon_points.accrued_points)
        self.assertEqual(5000, sale_order_coupon_points.max_accrued_points)
        self.assertEqual(500, loyalty_cart.accrued_points)
        self.assertEqual(5000, loyalty_cart.max_accrued_points)

    def test_accrual_points_no_max_point(self):
        self.year_end_rebate_program.rule_ids.reward_point_max_amount = 0
        self.year_end_rebate_program.rule_ids.flush_model(["reward_point_max_amount"])
        self.assertTrue(self.year_end_rebate_program.is_nominative)
        order = self._sell_product(self.product_A, 10)
        sale_order_coupon_points = order.coupon_point_ids
        loyalty_cart = sale_order_coupon_points.coupon_id
        self.assertEqual(1, len(sale_order_coupon_points))
        self.assertEqual(0.0, sale_order_coupon_points.accrued_points)
        self.assertEqual(0.0, loyalty_cart.max_accrued_points)
        self.assertEqual(0.0, loyalty_cart.accrued_points)
        self.assertEqual(0.0, loyalty_cart.max_accrued_points)
        # deliver partially the order
        self._deliver_order(order, self.product_A, 5)
        self.assertEqual(5.0, order.order_line[0].qty_delivered)
        self.assertEqual(500, sale_order_coupon_points.accrued_points)
        self.assertEqual(500, loyalty_cart.accrued_points)
        self.assertEqual(500, sale_order_coupon_points.max_accrued_points)
        self.assertEqual(500, loyalty_cart.max_accrued_points)

    def test_update_programs_and_rewards_recompute_total(self):
        order = self.so_with_loyalty
        loyalty_cart = order.coupon_point_ids.coupon_id
        self.assertEqual(1, len(order.coupon_point_ids))
        # unlink the coupon point
        loyalty_cart.sudo().unlink()
        order.coupon_point_ids.sudo().unlink()
        self.assertEqual(0, len(order.coupon_point_ids))
        # recomputes the coupon points
        order._update_programs_and_rewards()
        sale_order_coupon_points = order.coupon_point_ids
        loyalty_cart = sale_order_coupon_points.coupon_id
        self.assertEqual(1, len(order.coupon_point_ids))
        self.assertEqual(1000, sale_order_coupon_points.accrued_points)
        self.assertEqual(10000, sale_order_coupon_points.max_accrued_points)
        self.assertEqual(1000, loyalty_cart.accrued_points)
        self.assertEqual(10000, loyalty_cart.max_accrued_points)

    def test_update_programs_and_rewards_removing_coupon_point(self):
        order = self.so_with_loyalty
        self.assertEqual(1, len(order.coupon_point_ids))
        # we sell antoher product to ensure that a coupon point
        # will remain on for the partner
        rule_ids = self.year_end_rebate_program.rule_ids
        rule_ids.product_ids |= self.product_B
        order2 = self._sell_product(self.product_B, 10, partner=self.steve_bis)
        self._deliver_order(order2, self.product_B, 10)
        self.env.flush_all()

        sale_order_coupon_points = order.coupon_point_ids
        loyalty_cart = sale_order_coupon_points.coupon_id
        self.assertEqual(order2.coupon_point_ids.coupon_id, loyalty_cart)
        self.assertEqual(1000, sale_order_coupon_points.accrued_points)
        self.assertEqual(10000, sale_order_coupon_points.max_accrued_points)
        self.assertEqual(1050, loyalty_cart.accrued_points)
        self.assertEqual(10500, loyalty_cart.max_accrued_points)

        # we unlink the product A from the rule
        rule_ids.product_ids = self.product_B

        # recomputes the coupon points
        order._recompute_rfa(self.year_end_rebate_program)
        self.assertEqual(50, loyalty_cart.accrued_points)
        self.assertEqual(500, loyalty_cart.max_accrued_points)
