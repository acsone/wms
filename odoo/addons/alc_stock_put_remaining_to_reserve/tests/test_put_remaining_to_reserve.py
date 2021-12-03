# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPutRemainingToReserve(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPutRemainingToReserve, cls).setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "test product1",
                "default_code": "987654321",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654322",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.StockLocation = cls.env["stock.location"]

        cls.PickingType = cls.env["stock.picking.type"]
        cls.StockPicking = cls.env["stock.picking"]

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.vlb_location = cls.stock_location.location_id
        wh = cls.env.ref("stock.warehouse0")
        picking_sequence = wh.in_type_id.sequence_id

        reserve_medoc_root = cls.StockLocation.create(
            {
                "name": "Reserve Medoc Root",
                "location_id": cls.vlb_location.id,
                "usage": "internal",
                "act_as_view": True,
                "kind": "reserve",
            }
        )
        cls.picking_zone_medoc = cls.env["picking.zone"].create(
            {"code": "01", "name": "Medicament"}
        )
        cls.picking_type_med = cls.PickingType.create(
            {
                "name": "Pick Med",
                "code": "internal",
                "picking_zone_id": cls.picking_zone_medoc.id,
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
            }
        )

        cls.location_medoc = cls.StockLocation.create(
            {
                "name": "Medicament",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
                "picking_zone_id": cls.picking_zone_medoc.id,
                "reserve_location_id": reserve_medoc_root.id,
            }
        )

        entree_location = cls.StockLocation.create(
            {
                "name": "Entree",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
            }
        )

        parking_medoc_root = cls.StockLocation.create(
            {
                "name": "Parking Medicaments",
                "usage": "internal",
                "act_as_view": True,
                "kind": "parking",
                "location_id": entree_location.id,
            }
        )

        cls.parking_medoc = cls.StockLocation.create(
            {
                "name": "T99",
                "kind": "parking",
                "usage": "internal",
                "location_id": parking_medoc_root.id,
                "picking_zone_id": cls.picking_zone_medoc.id,
                "zone": "G",
                "corridor": "F",
                "shelf": "80",
                "height": "E",
                "box": "3",
                "bin_checksum_1": "12",
                "bin_checksum_2": "12",
            }
        )
        cls.StockLocation._parent_store_compute()

        # Set a quantity in this parking
        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "new_quantity": 100,
                "location_id": cls.parking_medoc.id,
            }
        )
        update_qty_wizard.change_product_qty()

        # Set a quantity in this parking
        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product2.id,
                "product_tmpl_id": cls.product2.product_tmpl_id.id,
                "new_quantity": 200,
                "location_id": cls.parking_medoc.id,
            }
        )
        update_qty_wizard.change_product_qty()

        cls.zone_gustave = cls.StockLocation.create(
            {"name": "G", "location_id": cls.location_medoc.id}
        )

        # Create the reserve RM99 (GD80X1)
        cls.reserve_medoc = cls.StockLocation.create(
            {
                "name": "RM99",
                "kind": "reserve",
                "usage": "internal",
                "location_id": reserve_medoc_root.id,
                "picking_zone_id": cls.picking_zone_medoc.id,
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "X",
                "box": "1",
                "bin_checksum_1": "12",
                "bin_checksum_2": "12",
            }
        )
        cls.reserve_medoc._parent_store_compute()

        cls.rangement_medoc = cls.StockLocation.create(
            {
                "name": "GD80B1",
                "kind": "bin",
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "B",
                "box": "1",
                "location_id": cls.zone_gustave.id,
                "bin_checksum_1": "12",
                "bin_checksum_2": "12",
            }
        )
        cls.rangement_medoc._parent_store_compute()

    def test_00(self):
        """
        Data:
            one picking, no existing picking for reserve
        Test case:
            put 30 pieces in stock and the 10 last goes to reserve
        Expected result:
            one picking to reserve is created and the 10 pieces are sent to reserve
        """
        picking = self.StockPicking.create(
            {
                "picking_type_id": self.picking_type_med.id,
                "location_id": self.parking_medoc.id,
                "location_dest_id": self.rangement_medoc.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 40,
                            "location_id": self.parking_medoc.id,
                            "location_dest_id": self.rangement_medoc.id,
                        },
                    )
                ],
            }
        )

        picking.action_assign()
        picking.action_confirm()
        for pack_op in picking.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty - 10

        picking_to_reserve = self.env["stock.picking"].search(
            [("picking_reserve_id", "=", picking.id)]
        )
        self.assertFalse(picking_to_reserve)
        pack_ops = picking.mapped("pack_operation_ids")
        pack_ops[0].action_put_in_reserve()

        picking_to_reserve = self.env["stock.picking"].search(
            [("picking_reserve_id", "=", picking.id)]
        )
        self.assertEqual(len(picking_to_reserve.move_lines), 1)

        move_to_reserve = picking_to_reserve.move_lines[0]
        self.assertEqual(move_to_reserve.product_qty, 10)

    def test_01(self):
        """
        Data:
            one picking for 2 products, no existing picking for reserve
        Test case:
            put 15 pieces of the first product in stock and the 25 last goes to reserve
            then, put 80 pieces of the second product in stock, the last 20 goes to reserve
        Expected result:
            one picking to reserve is created with the first product, then
            a new line for the second one is added to the reserve picking
        """

        picking2 = self.StockPicking.create(
            {
                "picking_type_id": self.picking_type_med.id,
                "location_id": self.parking_medoc.id,
                "location_dest_id": self.rangement_medoc.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 40,
                            "location_id": self.parking_medoc.id,
                            "location_dest_id": self.rangement_medoc.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.product2.name,
                            "product_id": self.product2.id,
                            "product_uom": self.product2.uom_id.id,
                            "product_uom_qty": 100,
                            "location_id": self.parking_medoc.id,
                            "location_dest_id": self.rangement_medoc.id,
                        },
                    ),
                ],
            }
        )

        picking2.action_assign()
        picking2.action_confirm()

        for pack_op in picking2.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty - 15

        pack_ops = picking2.mapped("pack_operation_ids")

        picking_to_reserve = self.env["stock.picking"].search(
            [("picking_reserve_id", "=", picking2.id)]
        )
        self.assertFalse(picking_to_reserve)

        pack_ops[0].action_put_in_reserve()
        picking_to_reserve = self.env["stock.picking"].search(
            [("picking_reserve_id", "=", picking2.id)]
        )
        self.assertEqual(len(picking_to_reserve.move_lines), 1)

        move_to_reserve_product1 = picking_to_reserve.move_lines[0]
        self.assertEqual(move_to_reserve_product1.product_qty, 15)

        pack_ops[1].action_put_in_reserve()
        self.assertEqual(len(picking_to_reserve.move_lines), 2)

        move_to_reserve_product2 = picking_to_reserve.move_lines[1]
        self.assertEqual(move_to_reserve_product2.product_qty, 15)
