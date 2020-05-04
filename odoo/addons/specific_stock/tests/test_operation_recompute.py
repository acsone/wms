# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import BaseCase


class TestOperationRecompute(BaseCase):
    def setUp(self):
        super(TestOperationRecompute, self).setUp()

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
        self.move_2 = self.env["stock.move"].create(
            {
                "picking_id": self.picking_1.id,
                "name": "Test move 2",
                "product_id": self.product_2.id,
                "product_uom": self.product_2.uom_id.id,
                "product_uom_qty": 1,
                "location_id": self.location.id,
                "location_dest_id": self.loc_customer.id,
                "date": "2018-01-01 00:00:00",
            }
        )
        self.move_2.action_confirm()

        # Put product in stock
        # - Product1 LotA: 3
        # - Product1 LotB: 5
        # - Product1 Additional: 20
        # - Product2: 10
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
                "product_qty": 3,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
                "prod_lot_id": self.product_1_lotA.id,
            }
        )
        inventory.line_ids.create(
            {
                "product_id": self.product_1.id,
                "product_qty": 5,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
                "prod_lot_id": self.product_1_lotB.id,
            }
        )
        inventory.line_ids.create(
            {
                "product_id": self.product_1_add.id,
                "product_qty": 20,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
            }
        )
        inventory.line_ids.create(
            {
                "product_id": self.product_2.id,
                "product_qty": 10,
                "inventory_id": inventory.id,
                "location_id": self.location.id,
            }
        )
        inventory.action_done()

        # There should be 2 quant in stock of product 1
        quants = self.env["stock.quant"].search(
            [("product_id", "=", self.product_1.id)]
        )
        self.assertEqual(len(quants), 2)
        # Force in_date for fifo
        quants[0].in_date = "2018-01-01 00:00:00"
        quants[1].in_date = "2018-01-02 00:00:00"

        self.picking_1.with_context(round_autoset=False).action_assign()

        quant = self.picking_1.move_lines.mapped("reserved_quant_ids")
        self.assertEqual(len(quant), 5)

        self.assertEqual(len(self.picking_1.pack_operation_ids), 3)
        self.op_product1 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_1
        )
        self.op_product1_add = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_1_add
        )
        self.op_product2 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_2
        )
        self.assertEqual(len(self.op_product1), 1)
        self.assertEqual(len(self.op_product1_add), 1)
        self.assertEqual(len(self.op_product2), 1)
        self.assertEqual(len(self.op_product1.pack_lot_ids), 2)

    def test_recompute_product1_before_additional(self):
        """ Recompute pack op of product1.
        Additional product not yet processed.
        Product 2 already processed 2"""
        self.op_product1.pack_lot_ids[0].qty = 1
        self.op_product1.save()
        self.op_product2.qty_done = 1

        qties = {}
        for op in self.picking_1.pack_operation_ids:
            if op.pack_lot_ids:
                qties[op.product_id.id] = {}
                for l in op.pack_lot_ids:
                    qties[op.product_id.id][l.lot_id.id] = (l.qty_todo, l.qty)
            else:
                qties[op.product_id.id] = (op.product_qty, op.qty_done)

        self.op_product1.linked_move_operation_ids.mapped("move_id").with_context(
            round_autoset=False
        )._recompute_pack_op()

        self.assertEqual(len(self.picking_1.pack_operation_ids), 3)

        new_op_product1 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_1
        )
        new_op_product1_add = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_1_add
        )
        new_op_product2 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_2
        )

        self.assertNotEqual(self.op_product1, new_op_product1)
        self.assertNotEqual(self.op_product1_add, new_op_product1_add)
        self.assertEqual(self.op_product2, new_op_product2)

        new_qties = {}
        for op in self.picking_1.pack_operation_ids:
            if op.pack_lot_ids:
                new_qties[op.product_id.id] = {}
                for l in op.pack_lot_ids:
                    new_qties[op.product_id.id][l.lot_id.id] = (l.qty_todo, l.qty)
            else:
                new_qties[op.product_id.id] = (op.product_qty, op.qty_done)

        self.assertEqual(qties, new_qties, "Done quantities have been lost")

    def test_recompute_product1_after_additional(self):
        """ Recompute pack op of product1.
        Additional product already processed.
        Product 2 already processed 2"""
        self.op_product1.pack_lot_ids[0].qty = 1
        self.op_product1.save()
        self.op_product1_add.qty_done = 1
        self.op_product2.qty_done = 1

        qties = {}
        for op in self.picking_1.pack_operation_ids:
            if op.pack_lot_ids:
                qties[op.product_id.id] = {}
                for l in op.pack_lot_ids:
                    qties[op.product_id.id][l.lot_id.id] = (l.qty_todo, l.qty)
            else:
                qties[op.product_id.id] = (op.product_qty, op.qty_done)

        self.op_product1.linked_move_operation_ids.mapped("move_id").with_context(
            round_autoset=False
        )._recompute_pack_op()

        self.assertEqual(len(self.picking_1.pack_operation_ids), 3)

        new_op_product1 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_1
        )
        new_op_product1_add = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_1_add
        )
        new_op_product2 = self.picking_1.pack_operation_ids.filtered(
            lambda o: o.product_id == self.product_2
        )

        self.assertNotEqual(self.op_product1, new_op_product1)
        self.assertEqual(self.op_product1_add, new_op_product1_add)
        self.assertEqual(self.op_product2, new_op_product2)

        new_qties = {}
        for op in self.picking_1.pack_operation_ids:
            if op.pack_lot_ids:
                new_qties[op.product_id.id] = {}
                for l in op.pack_lot_ids:
                    new_qties[op.product_id.id][l.lot_id.id] = (l.qty_todo, l.qty)
            else:
                new_qties[op.product_id.id] = (op.product_qty, op.qty_done)

        self.assertEqual(qties, new_qties, "Done quantities have been lost")
