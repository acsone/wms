# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockInventory(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockInventory, cls).setUpClass()
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.StockInventory = cls.env["stock.inventory"]
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")

        # Stockable product
        cls.product_stockable = cls.env["product.product"].create(
            {
                "type": "product",
                "name": "Stockable Product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
            }
        )

        cls._update_product_qty(cls.product_stockable)

    @classmethod
    def _update_product_qty(cls, product):
        product_qty = cls.env["stock.change.product.qty"].create(
            {
                "location_id": cls.stock_loc.id,
                "product_id": product.id,
                "new_quantity": 100.0,
            }
        )
        product_qty.change_product_qty()
        return product_qty

    def _get_inventory_values(self):
        return {"name": "test inventory"}

    def test_00(self):
        """
        Data:
            Nope
        Test case:
            Create a inventory without operator
            Start the inventory
        Expected result:
            The operator is not set
            The operator is set  to the current user
        """
        vals = self._get_inventory_values()
        vals.pop("operator_id", None)
        stock_inventory = self.StockInventory.create(vals)
        self.assertFalse(stock_inventory.operator_id)
        stock_inventory.prepare_inventory()
        self.assertEqual(stock_inventory.operator_id, self.env.user)

    def test_01(self):
        """
        Data:
            Nope
        Test case:
            Create a inventory with operator
            Start the inventory
        Expected result:
            The operator must be set to the given operator
            The operator is not updated...
        """
        vals = self._get_inventory_values()
        vals["operator_id"] = self.demo_user.id
        stock_inventory = self.StockInventory.create(vals)
        self.assertNotEqual(self.demo_user, self.env.user)
        self.assertEqual(stock_inventory.operator_id, self.demo_user)
        stock_inventory.prepare_inventory()
        self.assertEqual(stock_inventory.operator_id, self.demo_user)
