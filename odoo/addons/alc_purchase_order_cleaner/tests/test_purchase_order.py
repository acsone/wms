# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import SavepointCase


class TestPurchaseOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product_1 = cls.env["product.product"].create({"name": "Product 1"})
        cls.product_2 = cls.env["product.product"].create({"name": "Product 2"})

        cls.partner = cls.env.ref("base.res_partner_1")

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_planned": fields.Datetime.now(),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "product_qty": 365,
                            "price_unit": 50,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product_2.name,
                            "product_id": cls.product_2.id,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "product_qty": 0,
                            "price_unit": 5,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                ],
            }
        )

    def test_00(self):
        """
        Data:
            A PO with 2 lines:
            * line 1: product 1, product_qty 365
            * line 2: product 2, product_qty 0
        Test case:
            Confirm PO
        Expected result:
            line 2 is removed since the product_qty == 0
        """
        self.po.button_confirm()
        self.assertEqual(len(self.po.order_line), 1)
        self.assertEqual(self.po.order_line.product_id, self.product_1)
