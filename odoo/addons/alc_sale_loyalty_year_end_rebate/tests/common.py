# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon


class TestSaleLoyaltyYearEndRebateCommon(TestSaleCouponCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.year_end_rebate_program = cls.env["loyalty.program"].create(
            {
                "name": "Year-end Rebate",
                "applies_on": "both",
                "trigger": "auto",
                "program_type": "year_end_rebate",
                "rule_ids": [
                    Command.create(
                        {
                            "product_ids": cls.product_A,
                            "reward_point_amount": 1,
                            "reward_point_mode": "money",
                            "minimum_qty": 1,
                        }
                    )
                ],
                "reward_ids": [
                    Command.clear(),
                    Command.create(
                        {
                            "discount": 0,
                            "required_points": 1,
                            "reward_type": "rebate",
                        }
                    ),
                ],
                "communication_plan_ids": [Command.clear()],
            }
        )
