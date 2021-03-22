# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestReceiveFrigo(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReceiveFrigo, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, round_autoset=False))
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
        )

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        picking_sequence = cls.warehouse.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")

        cls.picking_zone_medoc = cls.env["picking.zone"].create(
            {"code": "01", "name": "Medicament"}
        )
        cls.location_medoc = cls.env["stock.location"].create(
            {
                "name": "Medicament",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
                "picking_zone_id": cls.picking_zone_medoc.id,
            }
        )

        cls.picking_type_medoc = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Médicaments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "subcode": "PICK",
                "groupbypartner": True,
                "color": 7,
                "sequence": 4,
                "picking_zone_id": cls.picking_zone_medoc.id,
            }
        )
        cls.route_medoc = cls.env["stock.location.route"].create(
            {
                "name": "Medicament",
                "pull_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "pull_medoc",
                            "location_id": location_out.id,
                            "picking_type_id": cls.picking_type_medoc.id,
                            "location_src_id": cls.location_medoc.id,
                            "procure_method": "make_to_stock",
                            "action": "move",
                        },
                    )
                ],
            }
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "medoc product",
                "default_code": "987654312",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.product_template1 = cls.product1.product_tmpl_id
        cls.product_template1.write({"route_ids": [(4, cls.route_medoc.id)]})

        cls.picking_zone_froid = cls.env["picking.zone"].create(
            {"code": "02", "name": "FROID/FRIGO"}
        )

        cls.location_froid = cls.env["stock.location"].create(
            {
                "name": "FROID/FRIGO",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
                "picking_zone_id": cls.picking_zone_froid.id,
            }
        )

        cls.picking_type_froid = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Médicaments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "subcode": "PICK",
                "groupbypartner": True,
                "color": 7,
                "sequence": 4,
                "picking_zone_id": cls.picking_zone_froid.id,
            }
        )
        cls.route_froid = cls.env["stock.location.route"].create(
            {
                "name": "FRIGO",
                "pull_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "pull_froid",
                            "location_id": location_out.id,
                            "picking_type_id": cls.picking_type_froid.id,
                            "location_src_id": cls.location_froid.id,
                            "procure_method": "make_to_stock",
                            "action": "move",
                        },
                    )
                ],
            }
        )
        cls.env["ir.model.data"].create(
            {
                "module": "__setup__",
                "name": "stock_location_route_pick_froid",
                "model": "stock.location.route",
                "res_id": cls.route_froid.id,
            }
        )

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "frigo product",
                "default_code": "12345789",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.product_template2 = cls.product2.product_tmpl_id
        cls.product_template2.write({"route_ids": [(4, cls.route_froid.id)]})

        cls.product3 = cls.env["product.product"].create(
            {
                "name": "frigo product2",
                "default_code": "12345789",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.product_template3 = cls.product3.product_tmpl_id
        cls.product_template3.write({"route_ids": [(4, cls.route_froid.id)]})

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "name": cls.product1.name,
                            "date_planned": "2017-07-17 12:42:12",
                            "product_qty": 12,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "price_unit": 42,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "name": cls.product2.name,
                            "date_planned": "2017-07-17 12:42:12",
                            "product_qty": 30,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "price_unit": 15,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product3.id,
                            "name": cls.product3.name,
                            "date_planned": "2017-07-17 12:42:12",
                            "product_qty": 30,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "price_unit": 15,
                        },
                    ),
                ],
            }
        )

    def test_00(self):
        """
        Data: one PO with products frigo and medoc
        Test case: we confirm the po and should have 2 receptions to do
        Expected: 2 receptions (pickings) :one for medoc, one for frigo
        """
        self.po.button_confirm()
        pickings = self.env["stock.picking"].search([("origin", "=", self.po.name)])
        self.assertEqual(len(pickings), 2)

    def test_01(self):
        """
        Data: one PO with products frigo and medoc
        Test case: we confirm the po and should have 2 receptions to do. A picking for frigo already exists
                    no new picking should be created for this one
        Expected: 2 receptions (pickings) :one for medoc, one for frigo
        """

        self.po.button_confirm()
        pickings = self.po.picking_ids
        self.assertEqual(len(pickings), 2)

        # Resetting the state of the PO : it goes all over again into the confirm
        # process, but pickings already exist
        self.po.state = "draft"
        self.po.button_confirm()

        pickings = self.po.picking_ids
        self.assertEqual(len(pickings), 2)
        picking_frigo = self.po.picking_ids.filtered(lambda x: x.is_picking_frigo)
        picking_medoc = self.po.picking_ids.filtered(lambda x: not x.is_picking_frigo)
        self.assertTrue(picking_frigo)
        self.assertTrue(picking_medoc)
