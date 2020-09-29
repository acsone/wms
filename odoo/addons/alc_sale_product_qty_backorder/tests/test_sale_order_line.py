# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleOrderLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderLine, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.sale_oder = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2018-01-29",
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 7,
                        },
                    )
                ],
            }
        )
        cls.order_line = cls.sale_oder.order_line[0]
        cls.sale_oder.action_confirm()

    def test_00(self):
        """
        Data:
            A sale order with a line with qty 7 and no product in stock
        Test case:
            1. Confirm the SO
            2. Cancel the line
        Expected result:
            1 product_qty_backorder == 7
              product_qty_remains_to_deliver == 7
              product_qty_canceled = 0
            2 Line is cancelled, no more backorder
              product_qty_backorder == 0
              product_qty_remains_to_deliver == 0
              product_qty_canceled == 7
        """

        order_line = self.order_line
        self.assertEqual(order_line.product_qty_backorder, 7)
        self.assertEqual(order_line.product_qty_remains_to_deliver, 7)
        self.assertEqual(order_line.product_qty_canceled, 0)
        order_line.write(
            {"product_qty_canceled": order_line.product_qty_remains_to_deliver}
        )
        self.assertEqual(order_line.product_qty_backorder, 0)
        self.assertEqual(order_line.product_qty_remains_to_deliver, 0)
        self.assertEqual(order_line.product_qty_canceled, 7)
