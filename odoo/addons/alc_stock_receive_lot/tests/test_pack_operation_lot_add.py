# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from .common import PackOperationLotAddCommon


class TestPackOperationLotAdd(PackOperationLotAddCommon, TransactionCase):
    def test_receive_on_view(self):
        picking = self.picking

        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).new({"picking_id": picking.id})

        op1 = picking.move_ids[0].move_line_ids[0]
        op2 = picking.move_ids[1].move_line_ids[0]

        # select operation
        wiz.move_line_id = op1
        self.assertEqual(5, wiz.remaining_qty)

        # select destination
        wiz.location_dest_id = self.bin1.id

        # receive first lot
        self.assertEqual(1, wiz.lot_required)
        wiz.lot_name = "Unittest Reception L1"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 3

        # go to next lot
        wiz.button_nextlot()

        self.assertEqual(op1, wiz.move_line_id)
        wiz._compute_remaining_qty()
        self.assertEqual(2, wiz.remaining_qty)
        self.assertEqual(self.bin1, wiz.location_dest_id)

        # receive second lot
        self.assertEqual(1, wiz.lot_required)
        wiz.lot_name = "Unittest Reception L2"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 1

        # go to next lot
        wiz.button_nextlot()
        wiz._compute_remaining_qty()
        self.assertEqual(op1, wiz.move_line_id)
        self.assertEqual(1, wiz.remaining_qty)
        self.assertEqual(self.bin1, wiz.location_dest_id)

        # receive again first lot
        self.assertEqual(1, wiz.lot_required)
        wiz.lot_name = "Unittest Reception L1"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 1

        # go to next operation
        wiz.button_nextop()
        self.assertFalse(wiz.move_line_id.id)
        self.assertFalse(wiz.lot_name)
        self.assertFalse(wiz.expiration_date)
        self.assertFalse(wiz.qty)

        # select operation
        wiz.move_line_id = op2
        # After next op, dest location is now reset
        wiz.location_dest_id = self.bin1
        self.assertEqual(5, wiz.remaining_qty)
        self.assertEqual(self.bin1, wiz.location_dest_id)

        # receive lot
        self.assertEqual(1, wiz.lot_required)
        wiz.lot_name = "Unittest Reception L3"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 5
        self.assertFalse(wiz.is_qty_exceeded)

        # go to next operation
        wiz.button_nextop()

        # validate
        picking.with_context(test_mode=True).button_validate()
        self.assertEqual("done", picking.state)
        self.assertEqual(len(self.products), len(picking.move_line_ids))

    def test_receive_surplus_quantities(self):
        picking = self.picking
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).create({"picking_id": picking.id})

        op1 = picking.move_ids[0].move_line_ids[0]

        # Simulate putaway to bin1 and bin2
        op1.location_dest_id = self.bin1

        # select operation
        with self.assertRaises(UserError), self.env.cr.savepoint():
            wiz.move_line_id = op1
            self.assertEqual(wiz.remaining_qty, 5)
            wiz.qty = 10
            wiz.lot_name = "Unittest Reception L1"
            wiz.button_nextop()
        wiz.move_line_id = op1
        self.assertEqual(wiz.remaining_qty, 5)
        wiz.qty = 10
        wiz.is_surplus_qty_confirmed = True
        wiz.lot_name = "Unittest Reception L1"
        wiz.button_nextop()
        self.assertEqual(op1.move_id.quantity_done, 10)

    def test_receive_lot_surplus_quantities(self):
        picking = self.picking
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).create({"picking_id": picking.id})

        op1 = picking.move_ids[0].move_line_ids[0]

        # Simulate putaway to bin1 and bin2
        op1.location_dest_id = self.bin1

        # select operation
        with self.assertRaises(UserError), self.env.cr.savepoint():
            wiz.move_line_id = op1
            self.assertEqual(wiz.remaining_qty, 5)
            self.assertTrue(wiz.lot_required)
            wiz.qty = 10
            wiz.expiration_date = "2030-01-01 10:00:00"
            wiz.lot_name = "Unittest Reception L1"
            wiz.button_nextop()
        wiz.move_line_id = op1
        self.assertTrue(wiz.lot_required)
        self.assertEqual(wiz.remaining_qty, 5)
        wiz.qty = 10
        wiz.lot_name = "Unittest Reception L1"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.is_surplus_qty_confirmed = True
        wiz.button_nextop()
        self.assertEqual(op1.move_id.quantity_done, 10)

    def test_receive_on_bins(self):
        picking = self.picking
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).create({"picking_id": picking.id})

        op1 = picking.move_ids[0].move_line_ids[0]
        op2 = picking.move_ids[1].move_line_ids[0]

        # Simulate putaway to bin1 and bin2
        op1.location_dest_id = self.bin1
        op2.location_dest_id = self.bin2

        # select operation
        wiz.move_line_id = op1
        self.assertEqual(wiz.remaining_qty, 5)

        # destination is already pre-selected
        self.assertEqual(wiz.location_dest_id, self.bin1)

        # change operation
        wiz.move_line_id = op2
        self.assertEqual(wiz.remaining_qty, 5)

        # destination has changed
        self.assertEqual(wiz.location_dest_id, self.bin2)

        # receive a lot
        self.assertEqual(wiz.lot_required, 1)
        wiz.lot_name = "Unittest Reception L1"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 1

        # go to next operation
        wiz.button_nextop()
        self.assertEqual(wiz.move_line_id.id, False)
        self.assertEqual(wiz.lot_name, False)
        self.assertEqual(wiz.expiration_date, False)
        self.assertEqual(wiz.qty, False)

        # select operation
        wiz.move_line_id = op1
        wiz.location_dest_id = self.bin1
        self.assertEqual(wiz.remaining_qty, 5)

        # destination is already pre-selected
        self.assertEqual(wiz.location_dest_id, self.bin1)

    def test_receive_no_lot_in_several_steps(self):
        no_lot_product = self.product_model.create(
            {
                "name": "Unittest Reception P3",
                "uom_id": self.ref("uom.product_uom_unit"),
                "tracking": "none",
                "barcode": "122345644322134",
            }
        )

        moves = self.env["stock.move"].create(
            [
                {
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.reception_location.id,
                    "name": "TEST MOVE RECEPTION ",
                    "product_id": no_lot_product.id,
                    "product_uom": no_lot_product.uom_id.id,
                    "product_uom_qty": 5.0,
                    "state": "waiting",
                }
            ]
        )

        picking = self.stock_picking_model.create(
            {
                "picking_type_id": self.ref("stock.picking_type_in"),
                "location_id": self.supplier_location.id,
                "location_dest_id": self.reception_location.id,
                "move_ids": moves.ids,
                "move_line_ids": moves.move_line_ids.ids,
            }
        )
        picking = picking.with_context(test_mode=1)
        picking.action_assign()
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).create({"picking_id": picking.id})

        op = picking.move_ids[0].move_line_ids[0]

        op.location_dest_id = self.bin1
        wiz.move_line_id = op
        self.assertEqual(wiz.location_dest_id, self.bin1)
        self.assertEqual(wiz.remaining_qty, 5)
        wiz.qty = 1
        wiz.button_nextop()
        wiz.move_line_id = op
        self.assertEqual(wiz.remaining_qty, 4)
        wiz.qty = 2
        wiz.button_nextop()
        wiz.move_line_id = op
        self.assertEqual(wiz.remaining_qty, 2)

    def test_recive_no_lot_change_destination(self):
        no_lot_product = self.product_model.create(
            {
                "name": "Unittest Reception P3",
                "uom_id": self.ref("uom.product_uom_unit"),
                "tracking": "none",
                "barcode": "122345644322134",
                "type": "product",
            }
        )

        moves = self.env["stock.move"].create(
            [
                {
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.reception_location.id,
                    "name": "TEST MOVE RECEPTION ",
                    "product_id": no_lot_product.id,
                    "product_uom": no_lot_product.uom_id.id,
                    "product_uom_qty": 5.0,
                    "state": "waiting",
                }
            ]
        )

        picking = self.stock_picking_model.create(
            {
                "picking_type_id": self.ref("stock.picking_type_in"),
                "location_id": self.supplier_location.id,
                "location_dest_id": self.reception_location.id,
                "move_ids": moves.ids,
                "move_line_ids": moves.move_line_ids.ids,
            }
        )
        picking = picking.with_context(test_mode=1)
        picking.action_assign()
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).create({"picking_id": picking.id})

        # select operation
        op = picking.move_ids.move_line_ids
        # we only have one operation
        self.assertEqual(len(op), 1)
        op.location_dest_id = self.bin1
        wiz.move_line_id = op

        # select destination
        wiz.location_dest_id = self.bin2.id

        self.assertNotEqual(op.location_dest_id, self.bin2)

        # receive qties
        wiz.qty = 3

        # go to next lot
        wiz.button_nextlot()

        # check destination
        self.assertEqual(op.location_dest_id, self.bin2)
        # do transfert and check product are in bin2

        # select an other destination
        new_bin = self.env["stock.location"].create(
            {
                "name": "New Bin",
                "location_id": self.env.ref("stock.stock_location_locations").id,
            }
        )

        wiz.location_dest_id = new_bin.id
        wiz.qty = 2
        wiz.button_nextlot()

        # we now have two operations
        op = picking.move_ids.move_line_ids
        self.assertEqual(len(op), 2)
        self.assertEqual(op[0].location_dest_id, self.bin2)
        self.assertEqual(op[1].location_dest_id, new_bin)

        wiz.button_transfer()

        quant_in_bin2 = self.env["stock.quant"].search(
            [
                ("product_id", "=", no_lot_product.id),
                ("location_id", "=", self.bin2.id),
            ]
        )
        self.assertEqual(quant_in_bin2.quantity, 3)
        quant_in_new_bin = self.env["stock.quant"].search(
            [
                ("product_id", "=", no_lot_product.id),
                ("location_id", "=", new_bin.id),
            ]
        )
        self.assertEqual(quant_in_new_bin.quantity, 2)

    def test_receive_existing_lot_surplus_quantities_aliment(self):
        """
        Create a lot with an expiration date for an aliment product.

        Then, do the reception with a surplus quantity
        The same lot should be used
        """
        self._create_lot()
        picking = self.picking
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).create({"picking_id": picking.id})

        op1 = picking.move_ids[0].move_line_ids[0]

        # Simulate putaway to bin1 and bin2
        op1.location_dest_id = self.bin1

        wiz.move_line_id = op1
        self.assertTrue(wiz.lot_required)
        self.assertEqual(wiz.remaining_qty, 5)
        wiz.qty = 10
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.is_surplus_qty_confirmed = True

        res_dict = wiz.button_transfer()
        # res_dict = picking.button_validate()
        # No backorder
        self.env["stock.backorder.confirmation"].with_context(
            **res_dict["context"]
        ).process_cancel_backorder()
        self.assertEqual(op1.move_id.quantity_done, 10)
        self.assertEqual(op1.move_id.lot_ids, self.created_lot)

    def _test_receive_lot(self, op, loc_bin, lot_name, qty, remaining_qty):
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).new({"picking_id": op.picking_id.id})
        wiz.move_line_id = op
        self.assertEqual(remaining_qty, wiz.remaining_qty)
        # select destination
        # receive first lot
        wiz.lot_name = lot_name
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = qty
        # go to next lot
        wiz.location_dest_id = loc_bin
        wiz.button_nextlot()

    def test_receive_same_lot_different_location(self):
        picking = self.stock_picking_model.create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.reception_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.reception_location.id,
                            "name": "TEST MOVE RECEPTION",
                            "product_id": self.products[0].id,
                            "product_uom": self.products[0].uom_id.id,
                            "product_uom_qty": 5.0,
                            "state": "waiting",
                        }
                    )
                ],
            }
        )
        picking.action_assign()
        self.assertEqual(len(picking.move_line_ids), 1)
        op = picking.move_line_ids
        self._test_receive_lot(op, self.bin1, "L1", 2, 5)
        self.assertEqual(len(picking.move_line_ids), 1)
        self._test_receive_lot(op, self.bin2, "L1", 2, 3)
        self.assertEqual(len(picking.move_line_ids), 2)
        self._test_receive_lot(op, self.bin1, "L1", 1, 1)
