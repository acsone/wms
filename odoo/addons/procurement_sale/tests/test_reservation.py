# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestReservation(TransactionCase):
    def setUp(self):
        super(TestReservation, self).setUp()

        self.product_1 = self.env["product.product"].create(
            {
                "name": "Product sale_procurement",
                "type": "product",
                "uom_id": self.env.ref("product.product_uom_unit").id,
                "uom_po_id": self.env.ref("product.product_uom_unit").id,
                "default_code": "Code product sale_procurement",
            }
        )

        wh = self.env["stock.warehouse"].search([])
        location = wh[0].view_location_id
        location.usage = "internal"
        loc_customer = self.env.ref("stock.stock_location_customers")

        pick_type = self.env.ref("stock.picking_type_out")
        pick_type.subcode = "PICK"

        # Create test move 1
        self.picking_1 = self.env["stock.picking"].create(
            {
                "picking_type_id": pick_type.id,
                "location_id": location.id,
                "location_dest_id": loc_customer.id,
            }
        )
        self.move_1 = self.env["stock.move"].create(
            {
                "picking_id": self.picking_1.id,
                "name": "Test move 1",
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_uom_qty": 2,
                "location_id": location.id,
                "location_dest_id": loc_customer.id,
                "date": "2018-01-01 00:00:00",
                "priority": "0",
            }
        )
        self.move_1.action_confirm()

        # Create test move 2
        self.picking_2 = self.env["stock.picking"].create(
            {
                "picking_type_id": pick_type.id,
                "location_id": location.id,
                "location_dest_id": loc_customer.id,
            }
        )
        self.move_2 = self.env["stock.move"].create(
            {
                "picking_id": self.picking_2.id,
                "name": "Test move 2",
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_uom_qty": 2,
                "location_id": location.id,
                "location_dest_id": loc_customer.id,
                "date": "2018-01-02 00:00:00",
                "priority": "0",
            }
        )
        self.move_2.action_confirm()

        # Put 1 product in stock
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test",
                "filter": "product",
                "location_id": location.id,
                "product_id": self.product_1.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.unlink()
        inventory.line_ids.create(
            {
                "product_id": self.product_1.id,
                "product_qty": 3.0,
                "inventory_id": inventory.id,
                "location_id": location.id,
            }
        )
        inventory.action_done()

        # There should be 1 quant in stock
        quants = self.env["stock.quant"].search(
            [("product_id", "=", self.product_1.id)]
        )
        self.assertEqual(len(quants), 1)
        self.assertTrue(quants.mapped("qty") == [3.0], "Unexpected quants qty in stock")
        self.assertEqual(self.product_1.qty_available, 3)

    def test_reservation_00(self):
        """
        Data:
            Qty in stock: 3
            Move 1: date 2018-01-01, priority 0, qty 2
            Move 2: date 2018-01-02, priority 0, qty 2
        Test case:
            Reserve move 1 then move 2.
        Expected result:
            Move 1: Reserved qty must be 2
            Move 2: Reserved qty must be 1
        -> Move 1 has been reserved before move 2 and date est prior to move 2
        """
        self.picking_1.with_context(round_autoset=False).action_assign()

        quant = self.move_1.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 2)

        quant = self.move_2.reserved_quant_ids
        self.assertEqual(len(quant), 0)

        self.picking_2.with_context(round_autoset=False).action_assign()

        quant = self.move_1.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 2)

        quant = self.move_2.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 1)

    def test_reservation_01(self):
        """
        Data:
            Qty in stock: 3
            Move 1: date 2018-01-01, priority 0, qty 2
            Move 2: date 2018-01-02, priority 0, qty 2
        Test case:
            Reserve move 2 then move 1.
        Expected result:
            Move 1: Reserved qty must be 2
            Move 2: Reserved qty must be 1
        -> Even if move 2 has been reserved before move 1, since the date of
        move 1 is prior to move 2, move 2 can't reserve qty required for move 1
        """
        self.picking_2.with_context(round_autoset=False).action_assign()

        quant = self.move_1.reserved_quant_ids
        self.assertEqual(len(quant), 0)

        quant = self.move_2.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 1)

        self.picking_1.with_context(round_autoset=False).action_assign()

        quant = self.move_1.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 2)

        quant = self.move_2.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 1)

    def test_reservation_03(self):
        """
        Data:
            Qty in stock: 3
            Move 1: date 2018-01-01, priority 0, qty 2
            Move 2: date 2018-01-02, priority 0, qty 2
        Test case:
            Set higher priority on move 2
            Reserve move 1 then move 2
        Expected result:
            Move 1: Reserved qty must be 1
            Move 2: Reserved qty must be 2
        -> Even if move 1 has been reserved before move 2, since the priority
        on move 2 is higher than move 1, move 1 can't consume qty required
        for move 2
        """
        self.move_2.priority = "1"
        self.picking_1.with_context(round_autoset=False).action_assign()

        quant = self.move_1.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 1)

        quant = self.move_2.reserved_quant_ids
        self.assertEqual(len(quant), 0)

        self.picking_2.with_context(round_autoset=False).action_assign()

        quant = self.move_1.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 1)

        quant = self.move_2.reserved_quant_ids
        self.assertEqual(len(quant), 1)
        self.assertEqual(quant.qty, 2)
