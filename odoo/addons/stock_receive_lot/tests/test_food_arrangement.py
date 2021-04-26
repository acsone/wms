# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestFoodArrangement(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestFoodArrangement, cls).setUpClass()

        cls.locationModel = cls.env["stock.location"]

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Unittest Reception P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "tracking": "lot",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Unittest Reception P2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "tracking": "lot",
            }
        )
        cls.products = [cls.product1, cls.product2]

        cls.supplier = cls.env["res.partner"].create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.reception_location = cls.locationModel.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "internal",
                "act_as_view": True,
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
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move 1",
                            "product_id": cls.product1.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product1.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.reception_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "move 2",
                            "product_id": cls.product2.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product2.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.reception_location.id,
                        },
                    ),
                ],
            }
        )
        cls.picking.action_assign()

        cls.stockReceptionWizard = cls.env["stock.pack.operation.lot.add"]

    def test_1(self):
        wiz = self.stockReceptionWizard.with_context(
            default_life_date_allowed=True
        ).new({"picking_id": self.picking.id})

        op1 = self.picking.pack_operation_product_ids[0]
        op2 = self.picking.pack_operation_product_ids[1]

        wiz.operation_id = op1
        wiz._onchange_operation_id()
        # select destination - it must be manually set
        self.assertEqual(wiz.location_dest_id.id, False)
        wiz.location_dest_id = self.bin1.id

        wiz.lot_name = "Unittest Reception L1"
        wiz.life_date = "2030-01-01 10:00:00"
        wiz.qty = 5

        self.assertEqual(wiz.location_dest_id, self.bin1)

        # go to next operation
        wiz.button_nextop()
        # Check location_dest_id is reset
        self.assertEqual(wiz.location_dest_id.id, False)

        # select operation
        wiz.operation_id = op2

        wiz._onchange_operation_id()
        # Check location is still unset, then manually set it.
        self.assertEqual(wiz.location_dest_id.id, False)
        wiz.location_dest_id = self.bin2.id

        wiz.lot_name = "Unittest Reception L2"
        wiz.life_date = "2030-01-01 10:00:00"
        wiz.qty = 5

        self.assertEqual(wiz.location_dest_id, self.bin2)
