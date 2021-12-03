# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestDateAnnounced(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestDateAnnounced, cls).setUpClass()

        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "product 1",
                "default_code": "12345789",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "product2",
                "default_code": "12345789",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
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
                ],
            }
        )

        cls.po.button_confirm()

    def test_00(self):
        """
        Check the date_announced is the same as the date_planned
        """

        line1 = self.po.order_line[0]
        line2 = self.po.order_line[1]

        self.assertEqual(line1.date_announced, line1.date_planned)
        self.assertEqual(line2.date_announced, line2.date_planned)

    def test_01(self):
        """
        Change date_announced, check it is changed and date_planned does not change
        """

        line1 = self.po.order_line[0]
        line2 = self.po.order_line[1]

        line1.write({"date_announced": "2017-07-25 12:42:12"})

        self.assertEqual(line1.date_announced, "2017-07-25 12:42:12")
        self.assertEqual(line1.date_planned, "2017-07-17 12:42:12")
        self.assertEqual(line2.date_announced, line2.date_planned)

    def test_02(self):
        """
        receive a part of a po : date should not be modified
        """

        line1 = self.po.order_line[0]
        line1.qty_received = 12.0
        picking = self.po.picking_ids[0]
        move1 = picking.move_lines[0]
        move1.state = "done"

        self.assertEqual(line1.qty_received, 12.0)
        self.assertFalse(line1.is_modify_date_announced_allowed)
