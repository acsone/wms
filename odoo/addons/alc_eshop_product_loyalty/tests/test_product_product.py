# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from freezegun import freeze_time

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductSchema(BaseCommon, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.product = cls.env["product.product"].create({"name": "test product"})
        cls.loyalty_program = cls.env["loyalty.program"].create(
            {
                "name": "test program",
                "date_from": "2023-01-01",
                "date_to": "2024-01-01",
                "active": True,
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

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)

        with freeze_time("2023-01-01"):
            product = ProductProduct.from_product_product(self.product)
            program_id = self.loyalty_program.id
            rules = product.loyalty_rules
            self.assertEqual(len(rules), 1)
            rule = rules[0]
            self.assertEqual(rule.sequence, 1001.0)
            self.assertEqual(rule.program_id, program_id)
            self.assertEqual(rule.time_frame.gte, date.fromisoformat("2023-01-01"))
            self.assertEqual(rule.time_frame.lte, date.fromisoformat("2024-01-01"))
            self.assertEqual(rule.id, self.loyalty_rule.id)

        with freeze_time("2024-01-02"):
            product = ProductProduct.from_product_product(self.product)
            program_id = self.loyalty_program.id
            self.assertEqual(len(product.loyalty_rules), 0)

        self.loyalty_program.active = False
        with freeze_time("2023-01-01"):
            product = ProductProduct.from_product_product(self.product)
            program_id = self.loyalty_program.id
            self.assertEqual(len(product.loyalty_rules), 0)
