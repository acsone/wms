# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax_10 = cls.env["account.tax"].create(
            {
                "name": "Percent tax",
                "amount_type": "percent",
                "amount": 10.0,
                "sequence": 3,
            }
        )
        cls.product_delivery_normal = cls.env["product.product"].create(
            {
                "name": "Normal Delivery Charges",
                "type": "service",
                "list_price": 10.0,
                "taxes_id": [(6, 0, [cls.tax_10.id])],
                "categ_id": cls.env.ref("delivery.product_category_deliveries").id,
            }
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Normal Delivery Charges",
                "fixed_price": 10,
                "delivery_type": "fixed",
                "product_id": cls.product_delivery_normal.id,
            }
        )

    def set_carrier(self, carrier):
        delivery_wizard = Form(
            self.env["choose.delivery.carrier"].with_context(
                default_order_id=self.sale_order.id,
                default_carrier_id=carrier.id,
            )
        )
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

    def test_sale_no_carrier(self):
        self.sale_order.carrier_id = False
        sale = Sale.from_sale_order(self.sale_order)
        self.assertIsNone(sale.delivery.method)
        self.assertIsNone(sale.delivery.fees)

    def test_sale_with_carrier(self):
        self.set_carrier(self.carrier)
        sale = Sale.from_sale_order(self.sale_order)
        method = sale.delivery.method
        self.assertIsNotNone(method)
        self.assertEqual(method.id, self.carrier.id)
        self.assertEqual(method.name, self.carrier.name)
        fees = sale.delivery.fees
        self.assertIsNotNone(fees)
        self.assertEqual(fees.tax, 1.0)
        self.assertEqual(fees.untaxed, 10.0)
        self.assertEqual(fees.total, 11.0)
        self.assertEqual(fees.discount_total, 0.0)
