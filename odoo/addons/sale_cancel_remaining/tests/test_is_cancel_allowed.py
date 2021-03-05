# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestIsCancelAllowed(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestIsCancelAllowed, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "product test 1",
                "type": "product",
                "default_code": "12345",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
            }
        )

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "product test 2",
                "type": "product",
                "default_code": "23456",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
            }
        )

        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product1.name,
                            "product_id": cls.product1.id,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "product_uom_qty": 10.0,
                            "price_unit": 50,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product2.name,
                            "product_id": cls.product2.id,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "product_uom_qty": 20.0,
                            "price_unit": 50,
                        },
                    ),
                ],
            }
        )
        cls.so1.action_confirm()

    def test_00(self):
        """
        Data: one SO for 2 products
        Test case: No qty delivered, no qty invoiced, 2 products
        Expected: cancel should be allowed
        """

        lines = self.so1.order_line
        for line in lines:
            self.assertEqual(line.is_cancel_remaining_allowed, True)

    def test_01(self):
        """
        Data: one SO for 2 products
        Test case: one product is invoiced already, the other is partially delivered
        Expected: cancel should not be allowed
        """

        lines = self.so1.order_line

        lines[0].qty_delivered = 10.0
        lines[1].qty_delivered = 10.0
        lines[1].qty_invoiced = 10.0
        for line in lines:
            self.assertEqual(line.is_cancel_remaining_allowed, False)

    def test_02(self):
        """
        Data: one SO for 2 products
        Test case: one product is partially delivered
        Expected: cancel should not be allowed on the partially delivered
        """

        lines = self.so1.order_line

        lines[0].qty_delivered = 10.0
        self.assertEqual(lines[0].is_cancel_remaining_allowed, False)
        self.assertEqual(lines[1].is_cancel_remaining_allowed, True)
