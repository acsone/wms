# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                queue_job__no_delay=True,
                # avoid failure when elasticsearch_security is installed
                es_security_no_autosync=True,
            )
        )
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
        cls._deliver_order(cls.so_with_loyalty, cls.product_A, 5)
        cls.empty_order = cls.env["sale.order"].create({"partner_id": cls.steve.id})
        return res

    @classmethod
    def _deliver_order(cls, order, product, qty):
        picking = order.picking_ids.filtered(lambda p: p.state == "assigned")
        move_ids = picking.move_ids.filtered(
            lambda l: l.product_id == product and l.state not in ["cancel", "done"]
        )
        move_ids.write({"quantity_done": qty})
        picking._action_done()

    def tests_so_no_loyalty(self):
        sale = Sale.from_sale_order(self.empty_order)
        self.assertEqual(sale.rebate_accrued_total_amount, 0.0)
        self.assertEqual(sale.rebate_accrued_total_max_amount, 0.0)
        self.assertEqual(sale.rebate_accrued_amount, 0.0)
        self.assertEqual(sale.rebate_accrued_max_amount, 0.0)
        self.assertEqual(sale.rebate_potential_amount, 0.0)
        self.assertEqual(sale.rebate_potential_max_amount, 0.0)

    def tests_so_with_loyalty(self):
        sale = Sale.from_sale_order(self.so_with_loyalty)
        self.assertEqual(sale.rebate_accrued_total_amount, 500.0)
        self.assertEqual(sale.rebate_accrued_total_max_amount, 5000.0)
        self.assertEqual(sale.rebate_accrued_amount, 500.0)
        self.assertEqual(sale.rebate_accrued_max_amount, 5000.0)
        self.assertEqual(sale.rebate_potential_amount, 1000.0)
        self.assertEqual(sale.rebate_potential_max_amount, 10000.0)
