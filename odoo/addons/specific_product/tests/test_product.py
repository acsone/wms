# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProduct, cls).setUpClass()

        # Create one product
        cls.product = cls.env["product.template"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "123321"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        # Create one reception for the product ==> one stock picking INCOMING but with 3 stock moves of the product
        picking_type_in_id = cls.env.ref("stock.picking_type_in").id
        location_id = cls.supplier_location.id
        location_dest_id = cls.stock_location.id

        # Create picking for product
        cls.picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type_in_id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
                "partner_id": cls.partner.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "a move",
                "product_id": cls.product.product_variant_ids.id,
                "product_uom_qty": 10,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking_in.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
            }
        )

        cls.env["stock.move"].create(
            {
                "name": "another move",
                "product_id": cls.product.product_variant_ids.id,
                "product_uom_qty": 5,
                "product_uom": cls.product.uom_id.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "picking_id": cls.picking_in.id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
            }
        )

        cls.env["stock.move"].create(
            {
                "name": "a last move",
                "product_id": cls.product.product_variant_ids.id,
                "product_uom_qty": 2,
                "product_uom": cls.product.uom_id.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "picking_id": cls.picking_in.id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
            }
        )

        # Create other moves for first product, on another picking
        cls.picking_in2 = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type_in_id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
                "partner_id": cls.partner.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "a move",
                "product_id": cls.product.product_variant_ids.id,
                "product_uom_qty": 10,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking_in2.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
            }
        )

        cls.env["stock.move"].create(
            {
                "name": "another move",
                "product_id": cls.product.product_variant_ids.id,
                "product_uom_qty": 5,
                "product_uom": cls.product.uom_id.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "picking_id": cls.picking_in2.id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
            }
        )

        cls.env["stock.move"].create(
            {
                "name": "a last move",
                "product_id": cls.product.product_variant_ids.id,
                "product_uom_qty": 2,
                "product_uom": cls.product.uom_id.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "picking_id": cls.picking_in2.id,
                "location_id": location_id,
                "location_dest_id": location_dest_id,
            }
        )

        cls.picking_in.action_confirm()
        cls.picking_in.action_assign()

        cls.picking_in2.action_confirm()
        cls.picking_in2.action_assign()

    def test_1(self):
        self.product._compute_incoming_pickings()

        # 2 pickings, 6 stock moves, the count should be 2
        self.assertEqual(self.product.count_pickings_to_do, 2)
