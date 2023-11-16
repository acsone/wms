# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tax = cls.env["account.tax"].create(
            {
                "amount_type": "percent",
                "amount": 10.0,
                "name": "Test Tax",
            }
        )
        cls.product.taxes_id = tax
        cls.sale_order.order_line.tax_id = tax

    def test_sale_with_discount(self):
        order_line = self.sale_order.order_line[0]
        order_line.price_unit = 30.75
        order_line.discount = 10.0
        order_line.discount2 = 10
        order_line.discount3 = 10
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertAlmostEqual(line.discount.rate, 27.1)
        self.assertAlmostEqual(line.discount.value, 9.17)
        self.assertEqual(line.unit_price.untaxed, 30.75)
        self.assertAlmostEqual(line.unit_price.untaxed_with_discount, 22.41675)
