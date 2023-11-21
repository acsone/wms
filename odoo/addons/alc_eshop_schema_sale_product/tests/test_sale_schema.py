# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    def tests_so_line_product(self):
        order_line = self.sale_order.order_line
        product = order_line.product_id
        product.default_code = False
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual(line.product.name, order_line.product_id.name)
        self.assertIsNone(line.product.sku)
        product.default_code = "skutest"
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual("skutest", line.product.sku)
