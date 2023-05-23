# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrderLineLots(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        StockLot = cls.env["stock.lot"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test Lot",
                "type": "product",
            }
        )
        cls.lot1 = StockLot.create(
            {
                "name": "Lot 1",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )

    @classmethod
    def _get_sale_order_line(cls):
        vals = {
            "product_id": cls.product.id,
        }
        return cls.env["sale.order.line"].new(vals)

    def test_sale_order_line_no_lot(self):
        # Create a new line with no quantity available
        # No lots on line
        line = self._get_sale_order_line()
        self.assertFalse(line.lot_ids)

    def test_sale_order_line_product(self):
        # Create a new line with quantity available but without lot
        # No lots on line
        self.env["stock.quant"].create(
            {
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product.id,
                "inventory_quantity": 5.0,
            }
        )._apply_inventory()
        line = self._get_sale_order_line()
        self.assertFalse(line.lot_ids)

    def test_sale_order_line_lot(self):
        # Create a new line with quantity available with lot
        # A lot on line
        self.env["stock.quant"].create(
            {
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": self.product.id,
                "inventory_quantity": 5.0,
                "lot_id": self.lot1.id,
            }
        )._apply_inventory()
        line = self._get_sale_order_line()
        self.assertTrue(line.lot_ids)
