# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestSaleLoyaltyYearEndRebateCommon


class TestSaleLoyaltyYearEndRebate(TestSaleLoyaltyYearEndRebateCommon):

    def test_rebate_uses_subtotal_price(self):
        self.assertFalse(self.year_end_rebate_program.coupon_ids)
        order = self.env["sale.order"].create(
            {
                "partner_id": self.steve.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_A.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        line = order.order_line[0]
        self.assertNotEqual(line.price_subtotal, line.price_total)
        self.assertEqual(1, len(self.year_end_rebate_program.coupon_ids))
        loyalty_cart = self.year_end_rebate_program.coupon_ids[0]
        self.assertEqual(line.price_subtotal, loyalty_cart.points)
