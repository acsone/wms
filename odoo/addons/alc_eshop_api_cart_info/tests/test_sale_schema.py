# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    def test_sale_no_client_ref(self):
        self.sale_order.client_order_ref = False
        sale = Sale.from_sale_order(self.sale_order)
        self.assertEqual(sale.customer_ref, None)

    def test_sale_with_client_ref(self):
        self.sale_order.client_order_ref = "my_ref"
        sale = Sale.from_sale_order(self.sale_order)
        self.assertEqual(sale.customer_ref, "my_ref")
