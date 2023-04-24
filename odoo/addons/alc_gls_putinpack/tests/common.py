# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.delivery_carrier_label_gls.tests.common import TestGLS


class TestGLSWizard(TestGLS):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        vals_product_1 = {"name": "product2", "type": "product", "weight": 1}
        vals_product_2 = {"name": "product2", "type": "product", "weight": 1}
        cls.product_1 = cls.env["product.product"].create(vals_product_1)
        cls.product_2 = cls.env["product.product"].create(vals_product_2)
        quants = cls.env["stock.quant"].create(
            {
                "location_id": cls.env.user._get_default_warehouse_id().lot_stock_id.id,
                "product_id": cls.product_1.id,
                "inventory_quantity": 100,
            }
        )
        quants |= cls.env["stock.quant"].create(
            {
                "location_id": cls.env.user._get_default_warehouse_id().lot_stock_id.id,
                "product_id": cls.product_2.id,
                "inventory_quantity": 100,
            }
        )
        quants.action_apply_inventory()
        vals_order_line_1 = {
            "name": "Line Description",
            "order_id": cls.sale_order.id,
            "product_id": cls.product_1.id,
        }
        vals_order_line_2 = {
            "name": "Line Description",
            "order_id": cls.sale_order.id,
            "product_id": cls.product_2.id,
        }
        cls.order_line_1 = cls.env["sale.order.line"].create(vals_order_line_1)
        cls.order_line_2 = cls.env["sale.order.line"].create(vals_order_line_2)
