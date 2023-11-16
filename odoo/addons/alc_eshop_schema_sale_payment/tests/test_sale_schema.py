# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_mode = cls.env.ref("account_payment_mode.payment_mode_inbound_dd1")

    def test_sale_no_payment(self):
        self.sale_order.payment_mode_id = None
        sale = Sale.from_sale_order(self.sale_order)
        self.assertIsNone(sale.payment.mode)

    def test_sale_with_paymen(self):
        self.sale_order.payment_mode_id = self.payment_mode
        sale = Sale.from_sale_order(self.sale_order)
        self.assertIsNotNone(sale.payment.mode)
        mode = sale.payment.mode
        self.assertEqual(mode.id, self.payment_mode.id)
        self.assertEqual(mode.name, self.payment_mode.name)
