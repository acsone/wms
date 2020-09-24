# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.tests.common import TransactionCase


class TestCron(TransactionCase):
    def setUp(self):
        super(TestCron, self).setUp()

        self.warehouse_1 = self.env.ref("stock.warehouse0")
        self.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "BWH",
            }
        )

        self.warehouse_1.pick_type_id.subcode = "PICK"

        self.SaleOrder = self.env["sale.order"]

        self.partner = self.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777874"}
        )

        self.p1 = self.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": self.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        self.p2 = self.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": self.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )

        self.so_after_3months_to_purge = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse_1.id,
                "date_order": datetime.datetime(2020, 3, 10).strftime("%Y-%m-%d"),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom_qty": 2,
                            "product_uom": self.p1.uom_id.id,
                            "price_unit": 1,
                            "is_consignment": False,
                        },
                    )
                ],
            }
        )

        self.so_after_3months_to_keep = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse_1.id,
                "auto_finalize_processing": False,
                "date_order": datetime.datetime(2020, 5, 10).strftime("%Y-%m-%d"),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p2.name,
                            "product_id": self.p2.id,
                            "product_uom_qty": 6,
                            "product_uom": self.p2.uom_id.id,
                            "price_unit": 1,
                            "is_consignment": False,
                        },
                    )
                ],
            }
        )

        self.so_after_3months_to_purge.action_confirm()
        self.so_after_3months_to_keep.action_confirm()

    def test_00(self):
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
            self.so_after_3months_to_keep.order_line.product_qty_canceled, 0
        )
        self.assertEqual(
            self.so_after_3months_to_keep.order_line.product_qty_remains_to_deliver, 6
        )
