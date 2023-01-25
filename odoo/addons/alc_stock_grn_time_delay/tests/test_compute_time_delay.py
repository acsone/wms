# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

from odoo.tests.common import TransactionCase


class TestComputeTimeDelay(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fake_grn_date = date(year=2020, month=8, day=10)
        fake_grn_date2 = date(year=2020, month=11, day=14)
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.ref = "888534954"
        cls.product = cls.env.ref("product.product_product_25")
        cls.grn = cls.env["stock.grn"].create(
            {
                "carrier_id": cls.partner.id,
                "date": fake_grn_date,
                "delivery_note_supplier_number": "12345678",
            }
        )

        cls.grn2 = cls.env["stock.grn"].create(
            {
                "carrier_id": cls.partner.id,
                "date": fake_grn_date2,
                "delivery_note_supplier_number": "12345655",
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
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
                "location_dest_id": cls.warehouse.view_location_id.id,
                "grn_id": cls.grn.id,
                "move_ids": [
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

        cls.stock_picking2 = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.warehouse.view_location_id.id,
                "grn_id": cls.grn2.id,
                "move_ids": [
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
        cls.env["res.config.settings"].create(
            {
                "max_delay_to_process_receipt": 7,
            }
        ).execute()

    @freeze_time("2020-10-26")
    def test_1(self):
        expected_delay = 55
        self.assertEqual(self.stock_picking.time_delay, expected_delay)
        self.assertTrue(self.stock_picking.is_time_exceeded)

    @freeze_time("2020-11-17")
    def test_2(self):
        expected_delay = 1
        self.assertEqual(self.stock_picking2.time_delay, expected_delay)
        self.assertFalse(self.stock_picking2.is_time_exceeded)
