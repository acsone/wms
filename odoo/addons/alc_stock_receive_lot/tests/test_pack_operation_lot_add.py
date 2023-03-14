# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPackOperationLotAdd(TransactionCase):
    def setUp(self):
        super().setUp()
        self.category_model = self.env["product.category"]
        self.product_model = self.env["product.product"]
        self.partner_model = self.env["res.partner"]

        # force parent_left/right computation
        self.location_model = self.env["stock.location"]
        # self.location_model.pool._init = False

        self.stock_picking_model = self.env["stock.picking"]
        self.stock_reception_wizard = self.env["stock.pack.operation.lot.add"]

        barcodes = ["1234567", "123453"]

        self.stock_location = self.location_model.create(
            {
                "name": "reception_parent",
                "usage": "internal",
            }
        )
        self.reception_location = self.location_model.create(
            {
                "name": "reception",
                "location_id": False,
                "usage": "view",
            }
        )

        self.products = self.product_model.create(
            [
                {
                    "name": "Unittest Reception P1",
                    "type": "product",
                    "uom_id": self.ref("uom.product_uom_unit"),
                    "tracking": "lot",
                    "barcode": barcodes[0],
                },
                {
                    "name": "Unittest Reception P2",
                    "type": "product",
                    "uom_id": self.ref("uom.product_uom_unit"),
                    "tracking": "lot",
                    "barcode": barcodes[1],
                },
            ]
        )

        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        for product in self.products:
            self.env["stock.quant"].with_context(inventory_mode=True).create(
                {
                    "product_id": product.id,
                    "location_id": warehouse.lot_stock_id.id,
                    "inventory_quantity": 50,
                }
            )._apply_inventory()

        self.supplier = self.partner_model.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        self.supplier_location = self.location_model.browse(
            self.ref("stock.stock_location_suppliers")
        )
        self.bin1 = self.location_model.create(
            {
                "name": "bin1",
                "location_id": self.reception_location.id,
                "usage": "internal",
            }
        )
        self.bin2 = self.location_model.create(
            {
                "name": "bin2",
                "location_id": self.reception_location.id,
                "usage": "internal",
            }
        )
        picking_type = self.env.ref("stock.picking_type_in")

        moves = self.env["stock.move"].create(
            [
                {
                    "location_id": self.supplier_location.id,
                    "location_dest_id": self.reception_location.id,
                    "name": "TEST MOVE RECEPTION ",
                    "product_id": product.id,
                    "product_uom": product.uom_id.id,
                    "product_uom_qty": 5.0,
                    "state": "waiting",
                }
                for product in self.products
            ]
        )
        picking = self.stock_picking_model.create(
            {
                "picking_type_id": picking_type.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.reception_location.id,
                "move_ids": moves.ids,
                "move_line_ids": moves.mapped("move_line_ids").ids,
            }
        )
        picking = picking.with_context(test_mode=1)
        picking.action_assign()
        self.picking = picking

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
        wiz._compute_move_line_id()
        self.assertEqual(5, wiz.remaining_qty)

        # select destination
        wiz.location_dest_id = self.bin1.id

        # receive first lot
        self.assertEqual(1, wiz.lot_required)
        wiz.lot_name = "Unittest Reception L1"
        wiz.expiration_date_char = "2030-01-01 10:00:00"
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
        wiz.expiration_date_char = "2030-01-01 10:00:00"
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
        wiz.expiration_date_char = "2030-01-01 10:00:00"
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
        wiz._compute_move_line_id()
        self.assertEqual(5, wiz.remaining_qty)
        self.assertEqual(self.bin1, wiz.location_dest_id)

        # receive lot
        self.assertEqual(1, wiz.lot_required)
        wiz.lot_name = "Unittest Reception L3"
        wiz.expiration_date_char = "2030-01-01 10:00:00"
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
            wiz._compute_move_line_id()
            self.assertEqual(wiz.remaining_qty, 5)
            wiz.qty = 10
            wiz.lot_name = "Unittest Reception L1"
            wiz.button_nextop()
        wiz.move_line_id = op1
        wiz._compute_move_line_id()
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
            wiz._compute_move_line_id()
            self.assertEqual(wiz.remaining_qty, 5)
            self.assertTrue(wiz.lot_required)
            wiz.qty = 10
            wiz.expiration_date = "2030-01-01 10:00:00"
            wiz.lot_name = "Unittest Reception L1"
            wiz.button_nextop()
        wiz.move_line_id = op1
        wiz._compute_move_line_id()
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
        wiz._compute_move_line_id()
        self.assertEqual(wiz.remaining_qty, 5)

        # destination is already pre-selected
        self.assertEqual(wiz.location_dest_id, self.bin1)

        # change operation
        wiz.move_line_id = op2
        wiz._compute_move_line_id()
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
        wiz._compute_move_line_id()
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
        wiz._compute_move_line_id()
        self.assertEqual(wiz.location_dest_id, self.bin1)
        self.assertEqual(wiz.remaining_qty, 5)
        wiz.qty = 1
        wiz.button_nextop()
        wiz.move_line_id = op
        wiz._compute_move_line_id()
        self.assertEqual(wiz.remaining_qty, 4)
        wiz.qty = 2
        wiz.button_nextop()
        wiz.move_line_id = op
        wiz._compute_move_line_id()
        self.assertEqual(wiz.remaining_qty, 2)
