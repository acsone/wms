# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProductTemplate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductTemplate, cls).setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.route_buy = cls.env.ref("purchase.route_warehouse0_buy")
        cls.picking_zone_medoc = cls.env.ref(
            "__setup__.picking_zone_medicament", raise_if_not_found=False
        )
        if not cls.picking_zone_medoc:
            cls.picking_zone_medoc = cls.env["picking.zone"].create(
                {"code": "01", "name": "Medicament"}
            )

        cls.picking_zone_ali = cls.env.ref(
            "__setup__.picking_zone_aliments", raise_if_not_found=False
        )
        if not cls.picking_zone_ali:
            cls.picking_zone_ali = cls.env["picking.zone"].create(
                {"code": "02", "name": "Aliment"}
            )

        cls.route_medoc = cls.env.ref(
            "__setup__.stock_location_route_pick_medoc", raise_if_not_found=False
        )

        cls.route_aliment = cls.env.ref(
            "__setup__.stock_location_route_pick_ali", raise_if_not_found=False
        )

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
        cls.zone_ali = cls.env["stock.location"].create(
            {"name": "A", "location_id": cls.location_ali.id}
        )

        cls.zone_gustave = cls.env["stock.location"].create(
            {"name": "G", "location_id": cls.location_medoc.id}
        )

        cls.location_product = cls.env["stock.location"].create(
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
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto").id

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "sale_ok": True,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
                "barcode": "XXX0001",
                "default_code": "12345",
            }
        )
        cls.product_template = cls.product.product_tmpl_id

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product without packaging",
                "sale_ok": True,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
                "barcode": "XXX0003",
                "default_code": "678910",
            }
        )
        cls.product_template1 = cls.product1.product_tmpl_id

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

        if not cls.route_aliment:
            cls.route_aliment = cls.env["stock.location.route"].create(
                {
                    "name": "Aliments",
                    "pull_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "pull_ali",
                                "location_id": location_out.id,
                                "picking_type_id": cls.picking_type_ali.id,
                                "location_src_id": cls.location_ali.id,
                                "procure_method": "make_to_stock",
                                "action": "move",
                            },
                        )
                    ],
                }
            )

        cls.route_new = cls.env.ref(
            "__setup__.stock_location_route_new", raise_if_not_found=False
        )

        if not cls.route_new:
            cls.route_new = cls.env["stock.location.route"].create(
                {"name": "Nouveautes"}
            )
            cls.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "stock_location_route_new",
                    "model": "stock.location.route",
                    "res_id": cls.route_new.id,
                }
            )
        cls.categ_ali = cls.env.ref("specific_data.product_categ_ali")
        cls.categ_ali.route_ids = [(4, cls.route_aliment.id)]
        if not cls.route_medoc:
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
        cls.categ_medoc = cls.env.ref("specific_data.product_categ_medoc")
        cls.categ_medoc.route_ids = [(4, cls.route_medoc.id)]

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

        cls.procurement_medoc = cls.env["procurement.order"].create(
            {
                "location_id": cls.location_medoc.id,
                "product_id": cls.product.id,
                "product_qty": 2.0,
                "product_uom": 1,
                "warehouse_id": cls.warehouse.id,
                "name": "proc_medoc",
                "origin": "test",
                "group_id": cls.group.id,
            }
        )

        cls.ProductPackaging = cls.env["product.packaging"]
        cls.product_palette = cls.ProductPackaging.create(
            {
                "packaging_type_id": cls.env.ref(
                    "alc_product_packaging.product_packaging_type_palette"
                ).id,
                "name": "Palette",
                "qty": 80,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.product_box = cls.ProductPackaging.create(
            {
                "packaging_type_id": cls.env.ref(
                    "alc_product_packaging.product_packaging_type_box"
                ).id,
                "name": "Box",
                "qty": 20,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )

    def test_1(self):
        " no min/max, and no route for 'approvisionner a la commande'"
        self.product_template._compute_min_max_and_on_command_reappro()
        self.assertTrue(self.product_template.no_min_max_no_on_command_reappro)

    def test_2(self):
        " min/max, and route for 'approvisionner a la commande' "
        self.product_template.write(
            {
                "orderpoint_min": 5,
                "orderpoint_max": 15,
                "route_ids": [(4, self.route_mto)],
            }
        )
        self.product_template._compute_min_max_and_on_command_reappro()
        self.assertTrue(self.product_template.min_max_on_command_reappro)

    def test_3(self):
        " not sale_ok but not archived"
        self.product_template.sale_ok = False
        self.product_template._compute_sale_not_ok_not_archived()
        self.assertTrue(self.product_template.sale_not_ok_not_archived)

    def test_4(self):
        " not sale_ok or archived but still has a bin"
        self.product_template.sale_ok = False
        self.product_template.write(
            {
                "sale_ok": False,
                "stock_bin_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "location_id": self.stock_location.id,
                            "bin_location_id": self.location_product.id,
                        },
                    )
                ],
            }
        )
        self.product_template._compute_sale_not_ok_archived_bin_available()
        self.assertTrue(self.product_template.sale_not_ok_archived_bin_available)

    def test_5(self):
        "mismatch routes/ picking zone"
        self.product_template.write(
            {"route_ids": [(6, 0, [self.route_aliment.id, self.route_medoc.id])]}
        )
        self.product_template._compute_mismatch_route_picking()
        self.assertTrue(self.product_template.mismatch_route_picking)

    def test_6(self):
        "mismatch picking zone / bin"

        self.product_template.write(
            {
                "route_ids": [(4, self.route_aliment.id)],
                "stock_bin_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "location_id": self.stock_location.id,
                            "bin_location_id": self.location_product.id,
                        },
                    )
                ],
            }
        )

        self.product_template._compute_mismatch_picking_bin()
        self.assertTrue(self.product_template.mismatch_picking_bin)

    def test_7(self):
        "can be bought without buy route"
        self.product_template.write(
            {"route_ids": [(3, self.route_buy.id)], "purchase_ok": True}
        )

        self.product_template._compute_can_be_bought_without_buy_route()
        self.assertTrue(self.product_template.can_be_bought_without_buy_route)

    def test_8(self):
        "route mto + route new"
        self.product_template.write(
            {"route_ids": [(6, 0, [self.route_mto, self.route_new.id])]}
        )

        self.product_template._compute_mto_with_abnormal_route()
        self.assertTrue(self.product_template.mto_with_abnormal_route)

    def test_9(self):
        "product without dimensions"

        self.product_template._compute_has_no_dimensions()
        self.assertTrue(self.product_template.has_no_dimensions)

        self.product_template.write({"height": 10.0, "width": 5.0, "length": 2.0})

        self.assertFalse(self.product_template.has_no_dimensions)

    def test_10(self):
        "product without packaging dimensions"

        self.product_template._compute_packaging_has_no_dimensions()
        self.assertTrue(self.product_template.packaging_has_no_dimensions)

        self.product_palette.write({"height": 100.0, "width": 50.0, "length": 20.0})
        self.assertTrue(self.product_template.packaging_has_no_dimensions)
        self.product_box.write({"height": 100.0, "width": 50.0, "length": 20.0})

        self.assertFalse(self.product_template.packaging_has_no_dimensions)

    def test_11(self):
        "product without packaging at all"

        self.product_template1._compute_packaging_has_no_dimensions()
        self.assertFalse(self.product_template1.packaging_has_no_dimensions)
