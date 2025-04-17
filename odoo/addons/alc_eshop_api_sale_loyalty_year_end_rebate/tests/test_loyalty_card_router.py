# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import freezegun

from odoo import Command

from odoo.addons.alc_eshop_total_year_end_rebate_partner_visibility.tests.common import (
    YearEndRebatePartnerVisibilityTestMixin,
)
from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import loyalty_card_router


class TestLoyaltyCardRouter(
    FastAPITransactionCase, YearEndRebatePartnerVisibilityTestMixin
):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls._setupRecords()
        cls.default_fastapi_router = loyalty_card_router
        cls.tax_15pc_excl = cls.env["account.tax"].create(
            {
                "name": "Tax 15%",
                "amount_type": "percent",
                "amount": 15,
                "type_tax_use": "sale",
            }
        )
        cls.product_A = cls.env["product.product"].create(
            {
                "name": "Product A",
                "list_price": 100,
                "sale_ok": True,
                "taxes_id": [(6, 0, [cls.tax_15pc_excl.id])],
            }
        )
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
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
            }
        )
        programs = cls.env["loyalty.program"].search(
            [("id", "!=", cls.year_end_rebate_program.id)]
        )
        cls.steve = cls.env["res.partner"].create(
            {
                "name": "Steve Bucknor",
                "email": "steve.bucknor@example.com",
            }
        )
        cls._allow_partner_to_see_total_year_end_rebate(partner=cls.steve, allow=True)
        programs.write({"active": False})
        cls.year_end_rebate_program.rule_ids.reward_point_max_amount = 10
        cls.steve_bis = cls.steve.copy({"name": "Steve Bis"})
        cls._allow_partner_to_see_total_year_end_rebate(cls.steve_bis, allow=True)
        with freezegun.freeze_time("2025-01-02 12:00:00"):
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
            cls._deliver_order(cls.so_with_loyalty, cls.product_A, 5)
            cls.empty_order = cls.env["sale.order"].create({"partner_id": cls.steve.id})

        cls.loyalty_card = cls.so_with_loyalty.coupon_point_ids.coupon_id

        return res

    @classmethod
    def _deliver_order(cls, order, product, qty):
        picking = order.picking_ids.filtered(lambda p: p.state == "assigned")
        move_ids = picking.move_ids.filtered(
            lambda l: l.product_id == product and l.state not in ["cancel", "done"]
        )
        move_ids.write({"quantity_done": qty})
        picking._action_done()

    @freezegun.freeze_time("2025-06-01 00:00:00")
    def test_get_loyalty_card_rfa_no_rfa(self):
        with self._create_test_client(partner=self.steve) as client:
            resonse = client.get("/loyalty/card/rfa/current")
            self.assertEqual(resonse.status_code, 204)

    @freezegun.freeze_time("2023-06-01 00:00:00")
    def test_get_loyalty_card_rfa_no_current(self):
        with self._create_test_client(
            partner=self.so_with_loyalty.partner_id
        ) as client:
            response = client.get("/loyalty/card/rfa/current")
            self.assertEqual(response.status_code, 204)

    @freezegun.freeze_time("2025-06-01 00:00:00")
    def test_get_loyalty_card_rfa_current(self):
        with self._create_test_client(
            partner=self.so_with_loyalty.partner_id
        ) as client:
            response = client.get("/loyalty/card/rfa/current")
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(
                {
                    "id": self.loyalty_card.id,
                    "program": {
                        "id": self.year_end_rebate_program.id,
                        "name": self.year_end_rebate_program.name,
                        "program_type": "year_end_rebate",
                        "date_from": "2025-01-01",
                        "date_to": "2025-12-31",
                    },
                    "points": 1000.0,
                    "accrued_points": 500.0,
                    "max_points": 10000.0,
                    "max_accrued_points": 5000.0,
                },
                response.json(),
            )

    @freezegun.freeze_time("2025-06-01 00:00:00")
    def test_get_loyalty_card_history(self):
        with self._create_test_client(
            partner=self.so_with_loyalty.partner_id
        ) as client:
            response = client.get(f"/loyalty/card/{self.loyalty_card.id}/history")
            self.assertEqual(response.status_code, 200)
            self.assertDictEqual(
                {
                    "count": 1,
                    "items": [
                        {
                            "order_id": self.so_with_loyalty.id,
                            "order_ref": self.so_with_loyalty.name,
                            "date_order": "2025-01-02T12:00:00",
                            "points": 1000.0,
                            "max_points": 10000.0,
                            "accrued_points": 500.0,
                            "max_accrued_points": 5000.0,
                        }
                    ],
                    "total": 1,
                },
                response.json(),
            )

    @freezegun.freeze_time("2025-06-01 00:00:00")
    def test_get_loyalty_card_history_no_history_no_access(self):
        with self._create_test_client(partner=self.steve) as client:
            response = client.get(f"/loyalty/card/{self.loyalty_card.id}/history")
            self.assertEqual(response.status_code, 404)

    @freezegun.freeze_time("2025-06-01 00:00:00")
    def test_loyalty_card_no_access(self):
        with self._create_test_client(
            partner=self.so_with_loyalty.partner_id
        ) as client:
            response = client.get("/loyalty/card/rfa/current")
            self.assertEqual(response.status_code, 200)
            response = client.get(f"/loyalty/card/{self.loyalty_card.id}/history")
            self.assertEqual(response.status_code, 200)
            self._allow_partner_to_see_total_year_end_rebate(
                self.so_with_loyalty.partner_id, allow=False
            )
            response = client.get("loyalty/card/rfa/current")
            self.assertEqual(response.status_code, 204)
            response = client.get(f"/loyalty/card/{self.loyalty_card.id}/history")
            self.assertEqual(response.status_code, 204)
