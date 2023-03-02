# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestDateAnnounced(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
        )

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "product 1",
                "default_code": "12345789",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "product2",
                "default_code": "12345789",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.today = datetime.today()
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner1.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product1.id,
                            "name": cls.product1.name,
                            "date_planned": cls.today,
                            "product_qty": 12,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 42,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": cls.product2.id,
                            "name": cls.product2.name,
                            "date_planned": cls.today,
                            "product_qty": 30,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "price_unit": 15,
                        },
                    ),
                ],
            }
        )

        cls.po.button_confirm()

    def test_00(self):
        """
        Data: 1 confirmed po with 2 lines.

        case: Check the date_announced is the same as the date_planned
        result: the date_announced is equal to the date_planned
        """

        line1 = self.po.order_line[0]
        line2 = self.po.order_line[1]

        self.assertEqual(line1.date_announced, line1.date_planned)
        self.assertEqual(line2.date_announced, line2.date_planned)

    def test_01(self):
        """
        Data: 1 confirmed po with 2 lines.

        case: Change date_announced of line 1
        result:
            line 1: date_announced has changed and date_planned hasn't
            line 2: both dates haven't changed
        """

        line1 = self.po.order_line[0]
        line2 = self.po.order_line[1]
        date_future = self.today + timedelta(days=10)
        line1.write({"date_announced": date_future})

        self.assertEqual(line1.date_announced, date_future)
        self.assertEqual(line1.date_planned, self.today)
        self.assertEqual(line2.date_announced, line2.date_planned)

    def test_02(self):
        """
        Data: 1 confirmed po with 2 lines.

        case: receive part of the po corresponding to line 1 and mark the move as done
        result: line 1 date_announced are not modifiable anymore
        """

        line1 = self.po.order_line[0]
        self.assertTrue(line1.is_modify_date_announced_allowed)
        line1.qty_received = 12.0
        picking = self.po.picking_ids[0]
        move1 = picking.move_ids[0]
        move1.state = "done"

        self.assertEqual(line1.qty_received, 12.0)
        self.assertFalse(line1.is_modify_date_announced_allowed)
