# -*- coding: utf-8 -*-
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestCancelPoNoMovesToReassign(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCancelPoNoMovesToReassign, cls).setUpClass()
        cls.partner_id = cls.env["res.partner"].create(
            {"name": "partner test", "ref": "84023435243"}
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )
        # Create moves coming from a PO:

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.vendor_location = cls.env.ref("stock.stock_location_suppliers")

        picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.vendor_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.move1 = cls.env["stock.move"].create(
            {
                "name": cls.product1.name,
                "product_id": cls.product1.id,
                "product_uom_qty": 1,
                "product_uom": cls.product1.uom_id.id,
                "picking_id": picking.id,
                "location_dest_id": cls.stock_location.id,
                "location_id": cls.vendor_location.id,
            }
        )
        cls.move2 = cls.env["stock.move"].create(
            {
                "name": cls.product2.name,
                "product_id": cls.product2.id,
                "product_uom_qty": 1,
                "product_uom": cls.product2.uom_id.id,
                "picking_id": picking.id,
                "location_dest_id": cls.stock_location.id,
                "location_id": cls.vendor_location.id,
            }
        )
        cls.moves = cls.move1 | cls.move2

    def test_no_move_to_reassign(self):
        """No moves to reassign since the location is not stock"""
        moves = self.moves._get_moves_to_auto_reassign()
        self.assertFalse(moves)
