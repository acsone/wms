# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleCartRestApiFlow(SchemaSaleCase):
    def test_qty_unavailable(self):
        self.sale_order.order_line.product_qty_unavailable = 1.0
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual(line.qty_unavailable, 1.0)

        self.sale_order.order_line.product_id.categ_id = self.env.ref(
            "alc_product_category_data.product_categ_humain"
        )
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual(line.qty_unavailable, 0.0)
