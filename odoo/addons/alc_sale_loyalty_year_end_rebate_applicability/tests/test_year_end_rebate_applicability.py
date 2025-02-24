# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import freezegun

from odoo import Command

from odoo.addons.alc_sale_loyalty_year_end_rebate.tests.common import (
    TestSaleLoyaltyYearEndRebateCommon,
)


class TestYearEndRebateApplicability(TestSaleLoyaltyYearEndRebateCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.veterinary_group_model = cls.env["veterinary.group"]
        cls.alcyonnaire_group = cls.veterinary_group_model.create(
            {"name": "Alcyonnaire", "is_alcyonnaire": True}
        )
        cls.partner_veterinary_with_contract = cls.partner_model.create(
            [
                {
                    "name": "Partner Veterinary under contract",
                    "veterinary_group_ids": [Command.link(cls.alcyonnaire_group.id)],
                    "date_start_contract_alcyonnaire": "2025-01-01",
                },
            ]
        )
        cls.rebate_2025 = cls.year_end_rebate_program
        cls.rebate_2025.write({"date_from": "2025-01-01", "date_to": "2025-12-31"})
        cls.rebate_2026 = cls.year_end_rebate_program.copy(
            {"date_from": "2026-01-01", "date_to": "2026-12-31"}
        )
        cls.rebate_2025.partner_domain = cls.rebate_2026.partner_domain = (
            '[("is_valid_vet_efficiency_member", "=", True)]'
        )
        cls.order_2025_01 = cls._create_order(
            cls.partner_veterinary_with_contract, "2025-01-01"
        )
        cls.order_2025_07 = cls._create_order(
            cls.partner_veterinary_with_contract, "2025-07-01"
        )
        cls.order_2026_01 = cls._create_order(
            cls.partner_veterinary_with_contract, "2026-01-01"
        )
        cls.order_2026_07 = cls._create_order(
            cls.partner_veterinary_with_contract, "2026-07-01"
        )
        cls.orders = (
            cls.order_2025_01
            | cls.order_2025_07
            | cls.order_2026_01
            | cls.order_2026_07
        )
        cls.env["loyalty.card"].search([]).unlink()

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

    def test_retroactive_program_on_existing_partner(self):
        self.assertEqual(0, len(self.rebate_2025.coupon_ids))
        self.assertEqual(0, len(self.rebate_2026.coupon_ids))

        with freezegun.freeze_time("2025-06-30"):
            # we make the partner elibile on 2025-06-30 with a start date of 2025-01-01
            # Only orders from 2025 should be rewarded since the program for 2026 is
            # not yet active
            self.partner_veterinary_with_contract.write(
                {
                    "date_start_contract_alcyonnaire": "2025-01-01",
                    "is_exclusive_vet_efficiency_member": True,
                }
            )

        self.assertEqual(1, len(self.rebate_2025.coupon_ids))
        self.assertEqual(0, len(self.rebate_2026.coupon_ids))
        so_coupont_points = self.env["sale.order.coupon.points"].search(
            [("order_id", "in", self.orders.ids)]
        )
        self.assertEqual(
            self.order_2025_01 | self.order_2025_07, so_coupont_points.order_id
        )
        self.assertEqual(self.rebate_2025, so_coupont_points.coupon_id.program_id)

    def test_program_removal_on_existing_partner_no_remove_past_card(self):
        with freezegun.freeze_time("2025-06-30"):
            # we make the partner elibile on 2025-06-30 with a start date of 2025-01-01
            # Only orders from 2025 should be rewarded since the program for 2026 is
            # not yet active
            self.partner_veterinary_with_contract.write(
                {
                    "date_start_contract_alcyonnaire": "2025-01-01",
                    "is_exclusive_vet_efficiency_member": True,
                }
            )

        self.assertEqual(1, len(self.rebate_2025.coupon_ids))
        self.assertEqual(0, len(self.rebate_2026.coupon_ids))

        # if I remove the eligibility in 2026, the coupon for 2025
        # should still be there
        with freezegun.freeze_time("2026-06-30"):
            self.partner_veterinary_with_contract.write(
                {"is_exclusive_vet_efficiency_member": False}
            )

        self.assertEqual(1, len(self.rebate_2025.coupon_ids))

    def test_program_removal_on_existing_partner_remove_current_card(self):
        with freezegun.freeze_time("2026-06-30"):
            # we make the partner elibile on 2025-06-30 with a start date of 2025-01-01
            # Only orders from 2025 should be rewarded since the program for 2026 is
            # not yet active
            self.partner_veterinary_with_contract.write(
                {
                    "date_start_contract_alcyonnaire": "2025-01-01",
                    "is_exclusive_vet_efficiency_member": True,
                }
            )

        self.assertEqual(0, len(self.rebate_2025.coupon_ids))
        self.assertEqual(1, len(self.rebate_2026.coupon_ids))

        # if I remove the eligibility in 2026, the coupon for 2025
        # should still be there
        with freezegun.freeze_time("2026-06-30"):
            self.partner_veterinary_with_contract.write(
                {"is_exclusive_vet_efficiency_member": False}
            )

        self.assertEqual(0, len(self.rebate_2025.coupon_ids))
        self.assertEqual(0, len(self.rebate_2026.coupon_ids))
