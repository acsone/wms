# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale.schemas import Sale
from odoo.addons.shopinvader_schema_sale.tests.common import SchemaSaleCase


class TestSaleSchema(SchemaSaleCase):
    def tests_so_no_qty_canceled(self):
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual(line.qty_canceled, 0.0)

    def tests_so_qty_canceled(self):
        self.sale_order.action_confirm()
        self.sale_order.action_done()
        wizard = self.env["sale.order.line.cancel"].create({})
        wizard.with_context(
            active_id=self.sale_order.order_line.id, active_model="sale.order.line"
        ).cancel_remaining_qty()
        sale = Sale.from_sale_order(self.sale_order)
        line = sale.lines[0]
        self.assertEqual(line.qty_canceled, 1.0)
