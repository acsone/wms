# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestTransferWizard(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestTransferWizard, cls).setUpClass()

        cls.picking_zone_medoc = cls.env["picking.zone"].create(
            {"code": "01", "name": "Medicament"}
        )
        cls.picking_zone_ali = cls.env["picking.zone"].create(
            {"code": "02", "name": "Aliment"}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.location_ali = cls.env["stock.location"].create(
            {
                "name": "Aliment",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
                "picking_zone_id": cls.picking_zone_ali.id,
            }
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
        cls.zone_gustave = cls.env["stock.location"].create(
            {"name": "G", "location_id": cls.location_medoc.id}
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "GD80B2",
                "kind": "bin",
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "B",
                "box": "2",
                "location_id": cls.zone_gustave.id,
                "bin_checksum_1": "45",
                "bin_checksum_2": "45",
            }
        )
        cls.env["stock.location"]._parent_store_compute()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        picking_sequence = cls.warehouse.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")
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

        cls.picking_type_ali = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Aliments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "subcode": "PICK",
                "groupbypartner": True,
                "color": 7,
                "sequence": 4,
                "picking_zone_id": cls.picking_zone_ali.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "test product1",
                "default_code": "123456789",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "immediately_usable_qty": 30,
            }
        )

        cls.product.stock_bin_ids.create(
            {
                "location_id": cls.stock_location.id,
                "bin_location_id": cls.location.id,
                "product_id": cls.product.product_tmpl_id.id,
            }
        )

        cls.group = cls.env["procurement.group"].create({"name": "test"})
        cls.procurement_ali = cls.env["procurement.order"].create(
            {
                "location_id": cls.location_ali.id,
                "product_id": cls.product.id,
                "product_qty": 2.0,
                "product_uom": 1,
                "warehouse_id": cls.warehouse.id,
                "name": "proc_ali",
                "origin": "test",
                "group_id": cls.group.id,
            }
        )

        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.location, 30.0
        )

    def test_00(self):
        """
        Data:
            A product  in a given zone with a given location
        Test case:
            Generate a wizard to move products from a location to a zone on the product.
        Expected result:
            a stock picking is created going from the location of the product to the location associated to the zone
        """

        wizard = self.env["alc.location.content.relocation.generator"].create(
            {"location_id": self.location.id}
        )
        res = wizard.dotransfer()
        stock_picking = self.env["stock.picking"].browse(res["res_id"])
        self.assertTrue(stock_picking)
        self.assertEqual(stock_picking.location_id.id, self.location.id)
        self.assertEqual(stock_picking.location_dest_id.id, self.stock_location.id)
