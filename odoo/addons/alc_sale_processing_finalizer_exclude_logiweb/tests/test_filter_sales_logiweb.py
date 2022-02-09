# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.tests.common import SavepointCase


class TestFilterSalesLogiweb(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestFilterSalesLogiweb, cls).setUpClass()
        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "BWH",
            }
        )

        cls.warehouse_1.pick_type_id.subcode = "PICK"

        cls.SaleOrder = cls.env["sale.order"]

        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777874"}
        )
        cls.logiweb_partner = cls.env.ref("alc_logiweb.logiweb_partner")
        cls.logiweb_be_partner = cls.env.ref("alc_logiweb.logiweb_be_partner")

        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )

        cls.so_after_3months_to_purge = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "date_order": datetime.datetime(2021, 9, 10).strftime("%Y-%m-%d"),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.p1.uom_id.id,
                            "price_unit": 1,
                            "is_consignment": False,
                        },
                    )
                ],
            }
        )
        cls.so_after_3months_logiweb = cls.SaleOrder.create(
            {
                "partner_id": cls.logiweb_partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "date_order": datetime.datetime(2021, 9, 10).strftime("%Y-%m-%d"),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.p2.name,
                            "product_id": cls.p2.id,
                            "product_uom_qty": 7,
                            "product_uom": cls.p2.uom_id.id,
                            "price_unit": 1,
                            "is_consignment": False,
                        },
                    )
                ],
            }
        )
        cls.so_after_3months_logiweb_be = cls.SaleOrder.create(
            {
                "partner_id": cls.logiweb_be_partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "date_order": datetime.datetime(2021, 9, 10).strftime("%Y-%m-%d"),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.p2.name,
                            "product_id": cls.p2.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.p2.uom_id.id,
                            "price_unit": 1,
                            "is_consignment": False,
                        },
                    )
                ],
            }
        )

    def test_00_check_logiweb_so_are_not_flushed(self):
        self.env["sale.order"].cancel_sales_bo_gt_3months()

        # Check that quantities for SO to purge have indeed been purged
        self.assertEqual(
            self.so_after_3months_to_purge.order_line.product_qty_canceled, 2
        )
        self.assertEqual(
            self.so_after_3months_to_purge.order_line.product_qty_remains_to_deliver, 0
        )

        # Check that quantities for SO to keep are still there
        self.assertEqual(
            self.so_after_3months_logiweb.order_line.product_qty_canceled, 0
        )
        self.assertEqual(
            self.so_after_3months_logiweb.order_line.product_qty_remains_to_deliver, 7
        )

        self.assertEqual(
            self.so_after_3months_logiweb_be.order_line.product_qty_canceled, 0
        )
        self.assertEqual(
            self.so_after_3months_logiweb_be.order_line.product_qty_remains_to_deliver,
            4,
        )
