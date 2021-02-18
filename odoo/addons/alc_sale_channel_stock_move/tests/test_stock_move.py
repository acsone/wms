# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMove, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "list_price": 20,
                "type": "product",
                "sale_ok": True,
                "active": False,
            }
        )
        # create a b2c_partner
        cls.partner = cls.env["res.partner"].create({"name": "test partner"})

        cls.b2c_order = cls.env["sale.order"].create(
            {
                "b2c_ref": 10,
                "sale_channel": "web",
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )

        cls.b2c_order.action_confirm()

    def test_00(self):

        pickings = self.b2c_order.picking_ids
        moves = pickings[0].move_lines

        self.assertEqual(moves[0].sale_channel, "web")
