# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command

from odoo.addons.shopinvader_search_engine.tests.common import TestProductBindingBase


class TestUpdate(TestProductBindingBase):
    """Test the update of loyalty program and loyalty rule."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                # avoid failure when elasticsearch_security is installed
                es_security_no_autosync=True,
            )
        )
        cls.loyalty_program = cls.env["loyalty.program"].create(
            {
                "name": "Loyalty Program",
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
            }
        )
        cls.loyalty_rule = cls.env["loyalty.rule"].create(
            {
                "name": "test rule",
                "sequence": 1.0,
                "program_id": cls.loyalty_program.id,
                "product_ids": [Command.link(cls.product.id)],
            }
        )
        cls.product_binding.state = "done"

    def test_update_loyalty_rule_on_active_program(self):
        with freeze_time("2025-01-01"):
            self.loyalty_rule.write({"sequence": 10})
            self.assertEqual(self.product_binding.state, "to_recompute")

    def test_update_loyalty_rule_on_inactive_program(self):
        with freeze_time("2026-01-01"):
            self.loyalty_rule.write({"sequence": 10})
            self.assertEqual(self.product_binding.state, "done")

    def test_update_loyalty_program(self):
        with freeze_time("2025-01-01"):
            self.loyalty_program.write({"date_from": "2024-01-01"})
            self.assertEqual(self.product_binding.state, "to_recompute")
