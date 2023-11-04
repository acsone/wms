# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    def tests_so_no_suite_name(self):
        sale = Sale.from_sale_order(self.sale_order)
        self.assertEqual(sale.suite_name, None)

    def tests_so_suite_name(self):
        self.sale_order.suite_name = "Suite Name"
        sale = Sale.from_sale_order(self.sale_order)
        self.assertEqual(sale.suite_name, "Suite Name")
