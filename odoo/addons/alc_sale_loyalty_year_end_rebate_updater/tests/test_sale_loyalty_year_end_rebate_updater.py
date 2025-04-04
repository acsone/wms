# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import freezegun

from odoo import Command

from odoo.addons.alc_sale_loyalty_year_end_rebate.tests.common import (
    TestSaleLoyaltyYearEndRebateCommon,
)


class TestSaleLoyaltyYearEndRebateUpdate(TestSaleLoyaltyYearEndRebateCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["loyalty.card"].search([]).sudo().unlink()
        cls.rebate_2025 = cls.year_end_rebate_program
        cls.rebate_2025.write({"date_from": "2025-01-01", "date_to": "2025-12-31"})
        cls.rebate_2025.partner_ids = cls.steve
        cls.rebate_2026 = cls.year_end_rebate_program.copy(
            {"date_from": "2026-01-01", "date_to": "2026-12-31"}
        )
        cls.order_2025_01 = cls._create_order(cls.steve, "2025-01-01")
        cls.order_2025_02 = cls._create_order(cls.steve, "2025-02-01", cls.product_B)
        cls.order_2025_07 = cls._create_order(cls.steve, "2025-07-01")
        cls.order_2025_09 = cls._create_order(cls.steve, "2025-09-01", cls.product_B)
        cls.order_2026_01 = cls._create_order(cls.steve, "2026-01-01")
        cls.order_2026_02 = cls._create_order(cls.steve, "2026-02-01", cls.product_B)
        cls.order_2026_07 = cls._create_order(cls.steve, "2026-07-01")
        cls.order_2026_09 = cls._create_order(cls.steve, "2026-09-01", cls.product_B)

        cls.orders = (
            cls.order_2025_01
            | cls.order_2025_02
            | cls.order_2025_07
            | cls.order_2025_09
            | cls.order_2026_01
            | cls.order_2026_02
            | cls.order_2026_07
            | cls.order_2026_09
        )
        cls.program_updater = cls.env["alc.loyalty.rule.updater"]

    @classmethod
    def _create_order(cls, partner, date_, product=None, qty=1):
        product = product or cls.product_A
        with freezegun.freeze_time(date_):
            order = cls.env["sale.order"].create(
                {
                    "partner_id": partner.id,
                    "order_line": [
                        (
                            0,
                            0,
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

    def _get_rfa_cards(self, program, partner):
        return program.coupon_ids.filtered(lambda c: c.partner_id == partner)

    def test_initial_situation(self):
        coupon_2025 = self._get_rfa_cards(self.rebate_2025, self.steve)
        coupon_2026 = self._get_rfa_cards(self.rebate_2026, self.steve)
        self.assertEqual(1, len(coupon_2025))
        self.assertEqual(1, len(coupon_2026))
        self.assertEqual(200, coupon_2025.points)  # (2 * 100 * 1 point for product A)
        self.assertEqual(
            200, coupon_2025.max_points
        )  # (2 * 100 * 1 point for product A)
        self.assertEqual(200, coupon_2026.points)  # (2 * 100 * 1 point for product A)
        self.assertEqual(
            200, coupon_2026.max_points
        )  # (2 * 100 * 1 point for product A)

    def test_add_rule(self):
        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "add_rule",
                            "new_reward_point_amount": 2,
                            "new_reward_point_max_amount": 3,
                            "added_product_ids": [Command.set(self.product_B.ids)],
                            "rule_name": "New rule",
                        },
                    )
                ],
            }
        )
        updater.do_update()
        # 2026 should not be impacted
        coupon_2026 = self._get_rfa_cards(self.rebate_2026, self.steve)
        self.assertEqual(1, len(coupon_2026))
        self.assertEqual(200, coupon_2026.points)
        self.assertEqual(200, coupon_2026.max_points)
        # 2025 should be impacted as
        # the order for product B is touched by the new rule
        # the order 2025_09 is updated to 10 points and 15 max points
        # since the retroactive date is 2025-06-30 and the order is on 2025-07-02
        # is not impacted by the new rule
        self.assertEqual(
            10, self.order_2025_09.coupon_point_ids.points
        )  # price 5, reward 2, qty 1
        self.assertEqual(
            15, self.order_2025_09.coupon_point_ids.max_points
        )  # price 5, reward 3, qty 1
        coupon_2025 = self._get_rfa_cards(self.rebate_2025, self.steve)
        self.assertEqual(1, len(coupon_2025))
        self.assertEqual(210, coupon_2025.points)
        self.assertEqual(215, coupon_2025.max_points)

    def test_remove_rule(self):
        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "remove_rule",
                            "loyalty_rule_id": self.rebate_2025.rule_ids.id,
                        },
                    )
                ],
            }
        )
        updater.do_update()
        # 2026 should not be impacted
        coupon_2026 = self._get_rfa_cards(self.rebate_2026, self.steve)
        self.assertEqual(1, len(coupon_2026))
        self.assertEqual(200, coupon_2026.points)
        self.assertEqual(200, coupon_2026.max_points)
        # 2025 should be impacted but only the order 2025_07
        coupon_2025 = self._get_rfa_cards(self.rebate_2025, self.steve)
        self.assertEqual(1, len(coupon_2025))
        self.assertEqual(100, coupon_2025.points)
        self.assertEqual(100, coupon_2025.max_points)

    def test_rule_update_points(self):
        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "rule_update_points",
                            "loyalty_rule_id": self.rebate_2025.rule_ids.id,
                            "new_reward_point_amount": 2,
                            "new_reward_point_max_amount": 3,
                        },
                    )
                ],
            }
        )
        updater.do_update()
        # 2026 should not be impacted
        coupon_2026 = self._get_rfa_cards(self.rebate_2026, self.steve)
        self.assertEqual(1, len(coupon_2026))
        self.assertEqual(200, coupon_2026.points)
        # 2025 should be impacted as
        # The first order for product A in 2025 is untouched (100 points and 100 max points)
        # The second order for product A in 2025 is updated to 200 points and 300 max points
        # since the retroactive date is 2025-06-30 and the order is on 2025-07-01
        self.assertEqual(100, self.order_2025_01.coupon_point_ids.points)
        self.assertEqual(100, self.order_2025_01.coupon_point_ids.max_points)
        self.assertEqual(200, self.order_2025_07.coupon_point_ids.points)
        self.assertEqual(300, self.order_2025_07.coupon_point_ids.max_points)
        coupon_2025 = self._get_rfa_cards(self.rebate_2025, self.steve)
        self.assertEqual(1, len(coupon_2025))
        self.assertEqual(300, coupon_2025.points)
        self.assertEqual(400, coupon_2025.max_points)

    def test_rule_add_remove_products(self):
        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "rule_add_products",
                            "loyalty_rule_id": self.rebate_2025.rule_ids.id,
                            "added_product_ids": [Command.set(self.product_B.ids)],
                        },
                    )
                ],
            }
        )
        updater.do_update()
        # 2026 should not be impacted
        coupon_2026 = self._get_rfa_cards(self.rebate_2026, self.steve)
        self.assertEqual(1, len(coupon_2026))
        self.assertEqual(200, coupon_2026.points)
        self.assertEqual(200, coupon_2026.max_points)
        # 2025 should be impacted as
        # the order for product B is touched by the new rule
        # the order 2025_09 is updated to 5 points and 10 max points
        self.assertEqual(
            5, self.order_2025_09.coupon_point_ids.points
        )  # price 5, reward 1, qty 1
        self.assertEqual(
            5, self.order_2025_09.coupon_point_ids.max_points
        )  # price 5, reward 1, qty 1
        coupon_2025 = self._get_rfa_cards(self.rebate_2025, self.steve)
        self.assertEqual(1, len(coupon_2025))
        self.assertEqual(205, coupon_2025.points)
        self.assertEqual(205, coupon_2025.max_points)

        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "rule_remove_products",
                            "loyalty_rule_id": self.rebate_2025.rule_ids.id,
                            "removed_product_ids": [Command.set(self.product_B.ids)],
                        },
                    )
                ],
            }
        )
        updater.do_update()
        self.assertEqual(0, self.order_2025_09.coupon_point_ids.points)
        self.assertEqual(0, self.order_2025_09.coupon_point_ids.max_points)
        self.assertEqual(1, len(coupon_2025))
        self.assertEqual(200, coupon_2025.points)
        self.assertEqual(200, coupon_2025.max_points)

    def test_multiple_updates(self):
        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "add_rule",
                            "new_reward_point_amount": 2,
                            "new_reward_point_max_amount": 3,
                            "added_product_ids": [Command.set(self.product_B.ids)],
                            "rule_name": "New rule",
                        },
                    ),
                    Command.create(
                        {
                            "update_type": "rule_update_points",
                            "loyalty_rule_id": self.rebate_2025.rule_ids.id,
                            "new_reward_point_amount": 2,
                            "new_reward_point_max_amount": 3,
                        },
                    ),
                ],
            }
        )
        updater.do_update()
        # 2026 should not be impacted
        coupon_2026 = self._get_rfa_cards(self.rebate_2026, self.steve)
        self.assertEqual(1, len(coupon_2026))
        self.assertEqual(200, coupon_2026.points)
        self.assertEqual(200, coupon_2026.max_points)
        # 2025 should be impacted as
        # the order for product B is touched by the new rule
        # the order 2025_09 is updated to 10 points and 15 max points
        # since the retroactive date is 2025-06-30 and the order is on 2025-07-02
        # is not impacted by the new rule
        self.assertEqual(
            10, self.order_2025_09.coupon_point_ids.points
        )  # price 5, reward 2, qty 1
        self.assertEqual(15, self.order_2025_09.coupon_point_ids.max_points)
        # The first order for product A in 2025 is untouched (100 points and 100 max points)
        # The second order for product A in 2025 is updated to 200 points and 300 max points
        # since the retroactive date is 2025-06-30 and the order is on 2025-07-01
        self.assertEqual(100, self.order_2025_01.coupon_point_ids.points)
        self.assertEqual(100, self.order_2025_01.coupon_point_ids.max_points)
        self.assertEqual(200, self.order_2025_07.coupon_point_ids.points)
        self.assertEqual(300, self.order_2025_07.coupon_point_ids.max_points)
        coupon_2025 = self._get_rfa_cards(self.rebate_2025, self.steve)
        self.assertEqual(1, len(coupon_2025))
        self.assertEqual(310, coupon_2025.points)
        self.assertEqual(415, coupon_2025.max_points)

    def test_added_product_ids_domain(self):
        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "add_rule",
                            "new_reward_point_amount": 2,
                            "new_reward_point_max_amount": 3,
                            "added_product_ids": [Command.set(self.product_B.ids)],
                            "rule_name": "New rule",
                        },
                    ),
                    Command.create(
                        {
                            "update_type": "rule_add_products",
                            "loyalty_rule_id": self.rebate_2025.rule_ids.id,
                            "added_product_ids": [Command.set(self.product_B.ids)],
                        },
                    ),
                ],
            }
        )
        add_rule_line = updater.line_ids[0]
        domain = add_rule_line.added_product_ids_domain
        products = self.env["product.product"].search(domain)
        self.assertTrue(products)
        for product in self.rebate_2025.rule_ids.product_ids:
            self.assertNotIn(product, products)

        rule_add_products_line = updater.line_ids[1]
        domain = rule_add_products_line.added_product_ids_domain
        products = self.env["product.product"].search(domain)
        self.assertTrue(products)
        for product in self.rebate_2025.rule_ids.product_ids:
            self.assertNotIn(product, products)

    def test_removed_product_ids_domain(self):
        updater = self.program_updater.create(
            {
                "loyalty_program_id": self.rebate_2025.id,
                "retroactive_date": "2025-06-30",
                "retroactive": True,
                "line_ids": [
                    Command.create(
                        {
                            "update_type": "rule_remove_products",
                            "loyalty_rule_id": self.rebate_2025.rule_ids.id,
                            "removed_product_ids": [Command.set(self.product_B.ids)],
                        },
                    ),
                ],
            }
        )
        remove_rule_line = updater.line_ids[0]
        domain = remove_rule_line.removed_product_ids_domain
        products = self.env["product.product"].search(domain)
        self.assertEqual(products, self.rebate_2025.rule_ids.product_ids)
