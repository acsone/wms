# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockProductionLot(SavepointCase):
    # to avoid trouble with pre installed db where specific_zeste is installed
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestStockProductionLot, cls).setUpClass()
        # enable lot
        cls.env.user.write(
            {"groups_id": [(4, cls.env.ref("stock.group_production_lot").id)]}
        )
        # product
        cls.prod1 = cls.env.ref("product.product_product_1")
        cls.prod2 = cls.prod1.copy()
        # Warehouses
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse1", "code": "WH1"}
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse2", "code": "WH2"}
        )

        # Locations
        cls.location_wh1_1 = cls.env["stock.location"].create(
            {
                "name": "TestLocation1",
                "location_id": cls.warehouse_1.view_location_id.id,
            }
        )
        cls.location_wh2_1 = cls.env["stock.location"].create(
            {
                "name": "TestLocation2",
                "location_id": cls.warehouse_2.view_location_id.id,
            }
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.location"]._parent_store_compute()

        # Lots
        StockProductionLot = cls.env["stock.production.lot"]
        cls.prod1_lot1 = StockProductionLot.create(
            {"name": "Prod 1 Lot 1", "product_id": cls.prod1.id}
        )
        cls.prod1_lot2 = StockProductionLot.create(
            {"name": "Prod 1 Lot 2", "product_id": cls.prod1.id}
        )
        cls.prod2_lot1 = StockProductionLot.create(
            {"name": "Prod 2 Lot 1", "product_id": cls.prod2.id}
        )
        cls.prod2_lot2 = StockProductionLot.create(
            {"name": "Prod 1 Lot 1", "product_id": cls.prod2.id}
        )
        cls.StockInventory = cls.env["stock.inventory"]

    def _add_lot_qty(self, prod_lot, qty, location):
        inventory_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": prod_lot.product_id.id,
                "new_quantity": qty,
                "location_id": location.id,
                "lot_id": prod_lot.id,
            }
        )
        inventory_wizard.change_product_qty()
        return

    def test_1(self):
        """
        Data:
            A product without stock (prod1)
        Test:
            1 Add qty 2  for lot1 in wh1
            2 Add qty 3 for lot1 in wh2
        Expected Results:
            1 qty_available = 2
              qty_available with wh1 into context = 2
              qty_available with wh2 into context = 0
            2 qty_available = 5
              qty_available with wh1 into context = 2
              qty_available with wh2 into context = 3
        """
        self.assertEqual(self.prod1_lot1.qty_available, 0)
        # 1
        self._add_lot_qty(self.prod1_lot1, 2, self.location_wh1_1)
        self.assertEqual(self.prod1_lot1.qty_available, 2)
        self.assertEqual(
            self.prod1_lot1.with_context(warehouse=self.warehouse_1.id).qty_available, 2
        )
        self.assertEqual(
            self.prod1_lot1.with_context(warehouse=self.warehouse_2.id).qty_available, 0
        )
        # 2
        self._add_lot_qty(self.prod1_lot1, 3, self.location_wh2_1)
        self.assertEqual(self.prod1_lot1.qty_available, 5)
        self.assertEqual(
            self.prod1_lot1.with_context(warehouse=self.warehouse_1.id).qty_available, 2
        )
        self.assertEqual(
            self.prod1_lot1.with_context(warehouse=self.warehouse_2.id).qty_available, 3
        )

    def test_2(self):
        """
        Data
            A product without stock (prod1)
        Test:
            Add qty 2 for lot1 in customer location
        Expected result:
            No stock available by default. Only available if we specify the
            location into the context
        """
        self.assertEqual(self.prod1_lot1.qty_available, 0)
        self._add_lot_qty(self.prod1_lot1, 2, self.customer_location)
        self.assertEqual(self.prod1_lot1.qty_available, 0)
        self.assertEqual(
            self.prod1_lot1.with_context(
                location=self.customer_location.id
            ).qty_available,
            2,
        )

    def test_3(self):
        """
        Data
            A product without stock (prod1)
        Test:
            Add qty for lot1 and lot2 into the same location
        Expectd result:
            Added qty = lot qty by lot
        """
        self.assertEqual(self.prod1_lot1.qty_available, 0)
        self._add_lot_qty(self.prod1_lot1, 2, self.location_wh1_1)
        self._add_lot_qty(self.prod1_lot2, 4, self.location_wh1_1)
        self.assertEqual(self.prod1_lot1.qty_available, 2)
        self.assertEqual(self.prod1_lot2.qty_available, 4)

    def test_4(self):
        """
        Data
            2 products without stock
        Tests:
            Add qty for one lot by product into the same location
        Expected result
            Added qty = lot qty by lot
        """
        self.assertEqual(self.prod1_lot1.qty_available, 0)
        self.assertEqual(self.prod2_lot1.qty_available, 0)
        self._add_lot_qty(self.prod1_lot1, 2, self.location_wh1_1)
        self._add_lot_qty(self.prod2_lot2, 4, self.location_wh1_1)
        self.assertEqual(self.prod1_lot1.qty_available, 2)
        self.assertEqual(self.prod2_lot2.qty_available, 4)
