# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestSaleOrderLine(SavepointCase):

    # to avoid trouble with pre installed db where specific_zeste is installed
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderLine, cls).setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.ref = "888534954"
        cls.prod1 = cls.env.ref("product.product_product_1")
        cls.prod2 = cls.prod1.copy()
        # Warehouses
        cls.warehouse_0 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse0", "code": "WH0"}
        )
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

        # Sale Orders / Lines
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2018-01-29",
                "client_order_ref": "whatever the client want",
                "warehouse_id": cls.warehouse_0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": cls.prod1.name,
                            "product_id": cls.prod1.id,
                            "product_uom_qty": 7,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "sequence": 2,
                            "name": cls.prod2.name,
                            "product_id": cls.prod2.id,
                            "product_uom_qty": 4,
                        },
                    ),
                ],
            }
        )

        cls.sol_prod1 = cls.so.order_line.filtered(
            lambda a, p=cls.prod1: a.product_id == p
        )
        cls.sol_prod2 = cls.so.order_line.filtered(
            lambda a, p=cls.prod2: a.product_id == p
        )

        # Stock pickings
        cls.StockPicking = cls.env["stock.picking"]
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_in_wh1 = cls.StockPicking.create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh1_1.id,
            }
        )
        cls.picking_in_wh2 = cls.StockPicking.create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh2_1.id,
            }
        )

        # Stock Moves
        cls.StockMove = cls.env["stock.move"]
        now = datetime.now()
        cls.dp1 = fields.Date.to_string(now + timedelta(days=1))
        cls.dp3 = fields.Date.to_string(now + timedelta(days=3))
        cls.dm1 = fields.Date.to_string(now - timedelta(days=1))
        # On WH0:
        # -> no stock move for prod1 and prod2
        # On WH1:
        # * 2 incoming moves for prod1 (d+1 , d+3)
        # * 2 incoming moves for prod2 (d-1 , d+1)
        cls.move_in_wh1_prod1_0 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh1.id,
                "product_id": cls.prod1.id,
                "product_uom_qty": 1,
                "product_uom": cls.prod1.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh1_1.id,
                "name": cls.prod1.name,
                "date_expected": cls.dp1,
            }
        )
        cls.move_in_wh1_prod1_1 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh1.id,
                "product_id": cls.prod1.id,
                "product_uom_qty": 2,
                "product_uom": cls.prod1.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh1_1.id,
                "name": cls.prod1.name,
                "date_expected": cls.dp3,
            }
        )
        cls.move_in_wh1_prod2_0 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh1.id,
                "product_id": cls.prod2.id,
                "product_uom_qty": 1,
                "product_uom": cls.prod2.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh1_1.id,
                "name": cls.prod2.name,
                "date_expected": cls.dm1,
            }
        )
        cls.move_in_wh1_prod2_1 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh1.id,
                "product_id": cls.prod2.id,
                "product_uom_qty": 2,
                "product_uom": cls.prod2.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh1_1.id,
                "name": cls.prod2.name,
                "date_expected": cls.dp1,
            }
        )
        # On WH2:
        # * 2 incoming moves for prod1 (d-1 , d+1)
        # * 2 incoming moves for prod2 (d+1 , d+3)
        cls.move_in_wh2_prod1_0 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh2.id,
                "product_id": cls.prod1.id,
                "product_uom_qty": 1,
                "product_uom": cls.prod1.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh2_1.id,
                "name": cls.prod1.name,
                "date_expected": cls.dm1,
            }
        )
        cls.move_in_wh2_prod1_1 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh2.id,
                "product_id": cls.prod1.id,
                "product_uom_qty": 2,
                "product_uom": cls.prod1.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh2_1.id,
                "name": cls.prod1.name,
                "date_expected": cls.dp1,
            }
        )
        cls.move_in_wh2_prod2_0 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh2.id,
                "product_id": cls.prod2.id,
                "product_uom_qty": 1,
                "product_uom": cls.prod2.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh2_1.id,
                "name": cls.prod2.name,
                "date_expected": cls.dp1,
            }
        )
        cls.move_in_wh2_prod2_1 = cls.StockMove.create(
            {
                "picking_id": cls.picking_in_wh2.id,
                "product_id": cls.prod2.id,
                "product_uom_qty": 2,
                "product_uom": cls.prod2.uom_id.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh2_1.id,
                "name": cls.prod2.name,
                "date_expected": cls.dp3,
            }
        )

    def test_01(self):
        """
        Data:
            An order with 2 products without incoming qty (warehouse_0)
        Test Case:
            Check next_expected_date_for_receipt
        Expected result:
            next_expected_date_for_receipt must be False
        """
        self.assertFalse(self.sol_prod1.next_expected_date_for_receipt)
        self.assertFalse(self.sol_prod2.next_expected_date_for_receipt)

    def test_02(self):
        """
        Data:
            An order with 2 products on warehouse_1
            A draft pricking in exists for the two products in warehouse_1
            and warehouse_2
        Test Case:
            1. Check next_expected_date_for_receipt
            2. Confirm the 2 pickings
        Expected result:
            1. next_expected_date_for_receipt must be False for the 2 products
            2. next_expected_date_for_receipt must be set for the 2 products
            at the min expected_date of the incoming stock move into wh1
        """
        self.so.warehouse_id = self.warehouse_1
        self.assertFalse(self.sol_prod1.next_expected_date_for_receipt)
        self.assertFalse(self.sol_prod2.next_expected_date_for_receipt)
        self.picking_in_wh1.action_confirm()
        self.picking_in_wh2.action_confirm()
        self.assertEqual(
            self.sol_prod1.next_expected_date_for_receipt, self.dp1
        )
        self.assertEqual(
            self.sol_prod2.next_expected_date_for_receipt, self.dm1
        )

    def test_03(self):
        """
        Data:
            An order with 2 products on warehouse_0
            A draft pricking in exists for the two products in warehouse_1
            and warehouse_2
        Test Case:
            1. Check next_expected_date_for_receipt
            2. Confirm the 2 pickings
            3. Assign warehouse_2 on the sale order
        Expected result:
            1. next_expected_date_for_receipt must be False for the 2 products
            2. next_expected_date_for_receipt must be False for the 2 products
            3. next_expected_date_for_receipt must be set for the 2 products
            at the min expected_date of the incoming stock move into wh2
        """
        self.assertFalse(self.sol_prod1.next_expected_date_for_receipt)
        self.assertFalse(self.sol_prod2.next_expected_date_for_receipt)
        self.picking_in_wh1.action_confirm()
        self.picking_in_wh2.action_confirm()
        self.assertFalse(self.sol_prod1.next_expected_date_for_receipt)
        self.assertFalse(self.sol_prod2.next_expected_date_for_receipt)
        self.so.warehouse_id = self.warehouse_2
        self.assertEqual(
            self.sol_prod1.next_expected_date_for_receipt, self.dm1
        )
        self.assertEqual(
            self.sol_prod2.next_expected_date_for_receipt, self.dp1
        )
