# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestLotLoss(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestLotLoss, cls).setUpClass()

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product stock_lot_loss",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "Code product lot_loss",
                "tracking": "lot",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2 stock_lot_loss no tracking",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "Code product lot_loss no tracking 2",
                "tracking": "none",
            }
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Product 3 stock_lot_loss no tracking",
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "uom_po_id": cls.env.ref("product.product_uom_unit").id,
                "default_code": "Code product lot_loss no tracking 3",
                "tracking": "none",
            }
        )
        wh = cls.env["stock.warehouse"].search([])
        cls.location = wh[0].view_location_id
        cls.location.usage = "internal"
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")

        cls.pick_type = cls.env.ref("stock.picking_type_out")
        cls.pick_type.subcode = "PICK"

    def initiate_values(self):
        self.product_1_lotA = self.env["stock.production.lot"].create(
            {"product_id": self.product_1.id, "name": "LotA"}
        )
        self.product_1_lotB = self.env["stock.production.lot"].create(
            {"product_id": self.product_1.id, "name": "LotB"}
        )

        # Create picking 1
        self.picking_1 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.pick_type.id,
                "location_id": self.location.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        self.move_1a = self.env["stock.move"].create(
            {
                "picking_id": self.picking_1.id,
                "name": "Test move 1a",
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_uom_qty": 6,
                "location_id": self.location.id,
                "location_dest_id": self.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        self.move_1a.action_confirm()
        self.move_1b = self.env["stock.move"].create(
            {
                "picking_id": self.picking_1.id,
                "name": "Test move 1b",
                "product_id": self.product_1.id,
                "product_uom": self.product_1.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.location.id,
                "location_dest_id": self.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        self.move_1b.action_confirm()

        # Put product in stock
        # LotA: 3
        # LotB: 5
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test",
                "filter": "product",
                "location_id": self.location.id,
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
                "location_id": self.location.id,
                "prod_lot_id": self.product_1_lotA.id,
            }
        )
        inventory.line_ids.create(
            {
                "product_id": self.product_1.id,
                "product_qty": 5.0,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
                "prod_lot_id": self.product_1_lotB.id,
            }
        )
        inventory.action_done()

        quants = self.env["stock.quant"].search(
            [("product_id", "=", self.product_1.id)]
        )
        self.assertEqual(len(quants), 2)

    def initiate_values_no_tracking(self):
        # Create picking 2
        self.picking_2 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.pick_type.id,
                "location_id": self.location.id,
                "location_dest_id": self.loc_customer.id,
            }
        )
        self.move_2 = self.env["stock.move"].create(
            {
                "picking_id": self.picking_2.id,
                "name": "Test move 2",
                "product_id": self.product_2.id,
                "product_uom": self.product_2.uom_id.id,
                "product_uom_qty": 6,
                "location_id": self.location.id,
                "location_dest_id": self.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        self.move_2.action_confirm()
        self.move_3 = self.env["stock.move"].create(
            {
                "picking_id": self.picking_2.id,
                "name": "Test move 3",
                "product_id": self.product_3.id,
                "product_uom": self.product_3.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.location.id,
                "location_dest_id": self.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        self.move_3.action_confirm()

        # Put product in stock
        # Product2: 3
        # Product3: 5
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test",
                "filter": "product",
                "location_id": self.location.id,
                "product_id": self.product_2.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.unlink()
        inventory.line_ids.create(
            {
                "product_id": self.product_2.id,
                "product_qty": 3.0,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
            }
        )
        inventory.line_ids.create(
            {
                "product_id": self.product_3.id,
                "product_qty": 5.0,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
            }
        )
        inventory.action_done()

        quants = self.env["stock.quant"].search(
            [("product_id", "in", (self.product_2.id, self.product_3.id))]
        )
        self.assertEqual(len(quants), 2)

    def test_lot_loss_line1(self):
        """ Create loss of line1 """
        # There should be 2 quant in stock
        self.initiate_values()

        self.picking_1.with_context(round_autoset=False).action_assign()

        quant = self.picking_1.move_lines.mapped("reserved_quant_ids")
        self.assertEqual(len(quant), 3)

        op = self.picking_1.pack_operation_ids
        self.assertEqual(len(op), 1)
        self.assertEqual(len(op.pack_lot_ids), 2)

        pack_lot_A = op.pack_lot_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )

        pack_lot_A.qty = 1
        op.save()

        op.with_context(round_autoset=False)._skip_operation(pack_op_lot_id=pack_lot_A)

        # Check new pack operation
        new_op = self.picking_1.pack_operation_ids
        self.assertNotEqual(op, new_op)
        self.assertEqual(len(new_op.pack_lot_ids), 2)

        new_pack_lot_A = new_op.pack_lot_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        new_pack_lot_B = new_op.pack_lot_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )

        self.assertEqual(new_pack_lot_A.qty_todo, 1)
        self.assertEqual(new_pack_lot_A.qty, 1)
        self.assertEqual(new_pack_lot_B.qty_todo, 5)
        self.assertEqual(new_pack_lot_B.qty, 0)

        # Check blocking move has been created
        loss_picking_type = self.env.ref("stock_lot_loss.stock_picking_type_23")
        block_move = (
            self.env["stock.quant"]
            .search(
                [
                    ("qty", ">", 0.0),
                    ("product_id", "=", self.product_1.id),
                    ("lot_id", "=", self.product_1_lotB.id),
                    ("location_id", "=", self.location.id),
                    (
                        "reservation_id.picking_id.picking_type_id",
                        "=",
                        loss_picking_type.id,
                    ),
                ]
            )
            .mapped("reservation_id")
        )
        self.assertEqual(block_move.ids, [])
        block_move = (
            self.env["stock.quant"]
            .search(
                [
                    ("qty", ">", 0.0),
                    ("product_id", "=", self.product_1.id),
                    ("lot_id", "=", self.product_1_lotA.id),
                    ("location_id", "=", self.location.id),
                    (
                        "reservation_id.picking_id.picking_type_id",
                        "=",
                        loss_picking_type.id,
                    ),
                ]
            )
            .mapped("reservation_id")
        )
        self.assertEqual(block_move.state, "assigned")
        self.assertEqual(block_move.product_qty, 2)

        # Check blocked lot cleanup
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test",
                "filter": "product",
                "location_id": self.location.id,
                "product_id": self.product_1.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.unlink()
        inventory.line_ids.create(
            {
                "product_id": self.product_1.id,
                "product_qty": 1.0,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
                "prod_lot_id": self.product_1_lotA.id,
            }
        )
        inventory.action_done()
        self.assertEqual(block_move.state, "cancel")

    def test_lot_loss_line2(self):
        """ Create loss of line2 """
        self.initiate_values()

        self.picking_1.with_context(round_autoset=False).action_assign()

        quant = self.picking_1.move_lines.mapped("reserved_quant_ids")
        self.assertEqual(len(quant), 3)

        op = self.picking_1.pack_operation_ids
        self.assertEqual(len(op), 1)
        self.assertEqual(len(op.pack_lot_ids), 2)

        pack_lot_A = op.pack_lot_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        pack_lot_B = op.pack_lot_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )

        pack_lot_A.qty = 3
        pack_lot_B.qty = 1
        op.save()

        op.with_context(round_autoset=False)._skip_operation(pack_op_lot_id=pack_lot_B)

        # Check new pack operation
        new_op = self.picking_1.pack_operation_ids
        self.assertNotEqual(op, new_op)
        self.assertEqual(len(new_op.pack_lot_ids), 2)

        new_pack_lot_A = new_op.pack_lot_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotA
        )
        new_pack_lot_B = new_op.pack_lot_ids.filtered(
            lambda line: line.lot_id == self.product_1_lotB
        )

        self.assertEqual(new_pack_lot_A.qty_todo, 3)
        self.assertEqual(new_pack_lot_A.qty, 3)
        self.assertEqual(new_pack_lot_B.qty_todo, 1)
        self.assertEqual(new_pack_lot_B.qty, 1)

        # Check blocking move has been created
        loss_picking_type = self.env.ref("stock_lot_loss.stock_picking_type_23")
        block_move = (
            self.env["stock.quant"]
            .search(
                [
                    ("qty", ">", 0.0),
                    ("product_id", "=", self.product_1.id),
                    ("lot_id", "=", self.product_1_lotA.id),
                    ("location_id", "=", self.location.id),
                    (
                        "reservation_id.picking_id.picking_type_id",
                        "=",
                        loss_picking_type.id,
                    ),
                ]
            )
            .mapped("reservation_id")
        )
        self.assertEqual(block_move.ids, [])
        block_move = (
            self.env["stock.quant"]
            .search(
                [
                    ("qty", ">", 0.0),
                    ("product_id", "=", self.product_1.id),
                    ("lot_id", "=", self.product_1_lotB.id),
                    ("location_id", "=", self.location.id),
                    (
                        "reservation_id.picking_id.picking_type_id",
                        "=",
                        loss_picking_type.id,
                    ),
                ]
            )
            .mapped("reservation_id")
        )
        self.assertEqual(block_move.state, "assigned")
        self.assertEqual(block_move.product_qty, 4)

        # Check blocked lot cleanup
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test",
                "filter": "product",
                "location_id": self.location.id,
                "product_id": self.product_1.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.unlink()
        inventory.line_ids.create(
            {
                "product_id": self.product_1.id,
                "product_qty": 1.0,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
                "prod_lot_id": self.product_1_lotB.id,
            }
        )
        inventory.action_done()
        self.assertEqual(block_move.state, "cancel")

    def test_loss_line_no_tracking(self):
        """ Create loss of product_2 without tracking"""
        self.initiate_values_no_tracking()

        self.picking_2.with_context(round_autoset=False).action_assign()

        quant = self.picking_2.mapped("move_lines.reserved_quant_ids")
        self.assertEqual(len(quant), 2)

        ops = self.picking_2.pack_operation_ids
        self.assertEqual(len(ops), 2)

        op_2 = ops.filtered(lambda op: op.product_id == self.product_2)
        op_3 = ops.filtered(lambda op: op.product_id == self.product_3)
        op_2.qty_done = 1.0
        op_3.qty_done = 1.0

        op_2.with_context(round_autoset=False)._skip_operation()
        # Check new pack operation
        new_op_2 = self.picking_2.pack_operation_ids.filtered(
            lambda op: op.product_id == self.product_2
        )
        self.assertNotEqual(op_2, new_op_2)
        self.assertEqual(new_op_2.product_qty, 1)
        self.assertEqual(new_op_2.qty_done, 1)

        # Check blocking move has been created
        loss_picking_type = self.env.ref("stock_lot_loss.stock_picking_type_23")
        block_move = (
            self.env["stock.quant"]
            .search(
                [
                    ("qty", ">", 0.0),
                    ("product_id", "=", self.product_3.id),
                    ("location_id", "=", self.location.id),
                    (
                        "reservation_id.picking_id.picking_type_id",
                        "=",
                        loss_picking_type.id,
                    ),
                ]
            )
            .mapped("reservation_id")
        )
        self.assertEqual(block_move.ids, [])
        block_move = (
            self.env["stock.quant"]
            .search(
                [
                    ("qty", ">", 0.0),
                    ("product_id", "=", self.product_2.id),
                    ("location_id", "=", self.location.id),
                    (
                        "reservation_id.picking_id.picking_type_id",
                        "=",
                        loss_picking_type.id,
                    ),
                ]
            )
            .mapped("reservation_id")
        )
        self.assertEqual(block_move.state, "assigned")
        self.assertEqual(block_move.product_qty, 2)

        # Check blocked lot cleanup
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Test",
                "filter": "product",
                "location_id": self.location.id,
                "product_id": self.product_1.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.unlink()
        inventory.line_ids.create(
            {
                "product_id": self.product_2.id,
                "product_qty": 1.0,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
            }
        )
        inventory.action_done()
        self.assertEqual(block_move.state, "cancel")

    def test_00(self):
        """
        Data:
            A picking with lines for un tracked products
        Test case:
            Skip all the operation a transfer the picking
        Expected result:
            The picking is done and a back_order is created
        """
        self.initiate_values_no_tracking()
        self.picking_2.with_context(round_autoset=False).action_assign()
        for op in self.picking_2.pack_operation_ids:
            op.action_missing_qty()
        self.picking_2.printed = True  # HACK TO GET THE STATE DONE.... TO BE REFACTORED
        result = self.picking_2.do_new_transfer()

        if isinstance(result, dict) and result:
            model = result.get("res_model")
            wizard = self.env[model].browse(int(result.get("res_id")))
            wizard.process()
        self.assertEqual(self.picking_2.state, "done")

    def test_01(self):
        """
        Data:
            A picking with lines for tracked products
        Test case:
            Skip all the operation a transfer the picking
        Expected result:
            The picking is confirmed and no pack op are available
        """
        self.initiate_values()
        self.picking_1.with_context(round_autoset=False).action_assign()
        pack_operations = self.picking_1.pack_operation_ids
        while pack_operations:
            pack_op = pack_operations[0]
            result = pack_op.action_missing_qty()
            if isinstance(result, dict) and result:
                model = result.get("res_model")
                wizard = (
                    self.env[model]
                    .with_context(result.get("context"))
                    .create({"skip_pack_lot_id": pack_op.pack_lot_ids.ids[0]})
                )
                wizard.doit()
            pack_operations = self.picking_1.pack_operation_ids

        self.picking_1.do_new_transfer()
        # if stock_picking_backorder is installed, a backorder is created and
        # the state is 'draft' HACK
        state = "draft" if "stock.backorder.reason" in self.env else "confirmed"
        self.assertEqual(self.picking_1.state, state)
        self.assertFalse(self.picking_1.pack_operation_ids)
        # here we try to create a backorder.
        self.picking_1._create_backorder()
        self.assertEqual(self.picking_1.state, "draft")

    def test_02(self):
        """
        Qty missing is only allowed on not incoming picking
        Data:
            A picking out with lines for tracked products
        Test case:
            1. Check if the action missing_qty is allowed.
            2. Change code on the picking_type to declare it as "incoming"
            3. Check if the action missing_qty is allowed.
        Expected results:
            1. True since the picking type code is != "incoming"
            2. False  since the picking type code is == "incoming"
        """
        self.initiate_values()
        self.picking_1.with_context(round_autoset=False).action_assign()
        self.assertTrue(
            all(
                self.picking_1.mapped(
                    "pack_operation_ids.is_action_missing_qty_allowed"
                )
            )
        )
        self.picking_1.picking_type_id.code = "incoming"
        self.assertFalse(
            all(
                self.picking_1.mapped(
                    "pack_operation_ids.is_action_missing_qty_allowed"
                )
            )
        )

    def test_03(self):
        """
        Data:
            A picking with lines for un tracked products
        Test case:
            Skip operation on a completed pack op
        Expected result:
            No error nor new picking
        """
        self.initiate_values_no_tracking()
        self.picking_2.with_context(round_autoset=False).action_assign()
        with self.assertRaises(UserError), self.env.cr.savepoint():
            for op in self.picking_2.pack_operation_ids:
                op.qty_done = op.product_qty
                op._skip_operation()
        for op in self.picking_2.pack_operation_ids:
            op.qty_done = op.product_qty
            op._skip_operation(raise_if_nothing_to_block=False)

    def test_04(self):
        """
        Data:
            A picking with lines for tracked products
        Test case:
            Skip operation on a completed pack op
        Expected result:
            No error nor new picking
        """
        self.initiate_values()
        self.picking_1.with_context(round_autoset=False).action_assign()
        with self.assertRaises(UserError), self.env.cr.savepoint():
            for op in self.picking_1.pack_operation_ids:
                for lot in op.pack_lot_ids:
                    lot.qty = lot.qty_todo
                    op._skip_operation(pack_op_lot_id=lot)

        for op in self.picking_1.pack_operation_ids:
            for lot in op.pack_lot_ids:
                lot.qty = lot.qty_todo
                op._skip_operation(pack_op_lot_id=lot, raise_if_nothing_to_block=False)
