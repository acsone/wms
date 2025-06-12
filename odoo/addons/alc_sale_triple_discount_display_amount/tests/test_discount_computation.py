# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestDiscountComputation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "service", "invoice_policy": "order"}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 10%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 10.0,
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.so_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.order.id,
                "product_id": cls.product.id,
                "name": "Line 1",
                "product_uom_qty": 1.0,
                "tax_id": [Command.set([cls.tax.id])],
                "price_unit": 1000.0,
            }
        )

    def test_discount_total_updates_with_discount(self):
        # discount_total = price * tax * discount_line1 = 1000 * 1.1 * 0.2
        self.so_line.discount = 20
        self.assertEqual(self.order.discount_total, 220)

        # price_total_no_discount = price * tax = 1000 * 1.1
        self.assertEqual(self.order.price_total_no_discount, 1100)

    def test_discount_total_updates_with_discount2(self):
        self.so_line.discount2 = 20
        self.assertEqual(self.order.discount_total, 220)
        self.assertEqual(self.order.price_total_no_discount, 1100)

    def test_discount_total_updates_with_discount3(self):
        self.so_line.discount3 = 20
        self.assertEqual(self.order.discount_total, 220)
        self.assertEqual(self.order.price_total_no_discount, 1100)

    def test_discount_total_updates_with_all_discounts(self):
        self.so_line.discount = 20
        self.so_line.discount2 = 20
        self.so_line.discount3 = 20

        self.so_line.discounting_type = "additive"
        # discout_total = 1000 * 1.1 * (0.2 + 0.2 + 0.2) = 660
        self.assertEqual(self.order.discount_total, 660)
        self.assertEqual(self.order.price_total_no_discount, 1100)
