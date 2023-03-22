# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFoodArrangement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.locationModel = cls.env["stock.location"]

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Unittest Reception P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "tracking": "lot",
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Unittest Reception P2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "tracking": "lot",
                "type": "product",
            }
        )
        cls.products = [cls.product1, cls.product2]

        cls.supplier = cls.env["res.partner"].create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        cls.stock_location = cls.env.ref("stock.stock_location_suppliers")

        cls.reception_location = cls.locationModel.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "view",
            }
        )
        cls.bin1 = cls.locationModel.create(
            {
                "name": "bin non mto",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        cls.bin2 = cls.locationModel.create(
            {
                "name": "bin mto",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        moves = cls.env["stock.move"].create(
            [
                {
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": cls.reception_location.id,
                    "name": "TEST MOVE RECEPTION ",
                    "product_id": product.id,
                    "product_uom": product.uom_id.id,
                    "product_uom_qty": 5.0,
                    "state": "waiting",
                }
                for product in cls.products
            ]
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_ids": moves.ids,
            }
        )
        cls.picking.action_assign()

        cls.stockReceptionWizard = cls.env["stock.pack.operation.lot.add"]

    def test_1(self):
        wiz = self.stockReceptionWizard.with_context(
            default_expiration_date_allowed=True
        ).new({"picking_id": self.picking.id})

        op1 = self.picking.move_ids[0].move_line_ids[0]
        op2 = self.picking.move_ids[1].move_line_ids[0]

        wiz.move_line_id = op1
        wiz.location_dest_id = self.bin2.id

        wiz.lot_name = "Unittest Reception L1"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 5

        self.assertEqual(wiz.location_dest_id, self.bin2)

        # go to next operation
        wiz.button_nextop()
        # Check location_dest_id is reset
        self.assertEqual(wiz.location_dest_id.id, False)

        # select operation
        wiz.move_line_id = op2

        wiz.location_dest_id = self.bin2.id

        wiz.lot_name = "Unittest Reception L2"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 5

        self.assertEqual(wiz.location_dest_id, self.bin2)
