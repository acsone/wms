# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    def tests_so_no_qty_unavailable(self):
        self.sale_order.order_line.product_qty_unavailable = False
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual(line.qty_unavailable, 0.0)

    def tests_so_qty_unavailable(self):
        self.sale_order.order_line.product_qty_unavailable = 1.0
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual(line.qty_unavailable, 1.0)
