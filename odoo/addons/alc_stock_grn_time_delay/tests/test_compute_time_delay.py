# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time
from odoo.tests.common import SavepointCase


class TestComputeTimeDelay(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestComputeTimeDelay, cls).setUpClass()
        fake_grn_date = datetime.strptime("2020-08-10 00:00:00", "%Y-%m-%d %H:%M:%S")
        fake_grn_date2 = datetime.strptime("2020-11-14 00:00:00", "%Y-%m-%d %H:%M:%S")
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.ref = "888534954"
        cls.product = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.grn = cls.env["stock.grn"].create(
            {"carrier_id": cls.partner.id, "date": fake_grn_date}
        )

        cls.grn2 = cls.env["stock.grn"].create(
            {"carrier_id": cls.partner.id, "date": fake_grn_date2}
        )
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {"name": "Warehouse1", "code": "WH1"}
        )
        cls.location_wh1_1 = cls.env["stock.location"].create(
            {
                "name": "TestLocation1",
                "location_id": cls.warehouse_1.view_location_id.id,
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        location_id = cls.supplier_location.id
        location_dest_id = cls.stock_location.id
        cls.stock_picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh1_1.id,
                "grn_id": cls.grn.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": location_id,
                            "location_dest_id": location_dest_id,
                        },
                    )
                ],
            }
        )
        cls.stock_picking.action_confirm()
        cls.stock_picking.force_assign()

        cls.stock_picking2 = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.location_wh1_1.id,
                "grn_id": cls.grn2.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": location_id,
                            "location_dest_id": location_dest_id,
                        },
                    )
                ],
            }
        )
        cls.stock_picking2.action_confirm()
        cls.stock_picking2.force_assign()

    @freeze_time("2020-10-26 00:00:00")
    def test_1(self):

        expected_delay = 55
        self.stock_picking._compute_time_delay()
        self.assertEqual(self.stock_picking.time_delay, expected_delay)

    @freeze_time("2020-11-17 00:00:00")
    def test_2(self):

        expected_delay = 1
        self.stock_picking2._compute_time_delay()
        self.assertEqual(self.stock_picking2.time_delay, expected_delay)
