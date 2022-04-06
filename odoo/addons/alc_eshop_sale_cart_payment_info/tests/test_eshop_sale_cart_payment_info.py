# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSaleCartRestPaymentInfoCase(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartRestPaymentInfoCase, cls).setUpClass()
        cls.payment_mode = cls.env.ref("account_payment_mode.payment_mode_inbound_dd1")
        with cls.cart_service(cls.partner_1.id) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {"uuid": "uuid1", "product_id": cls.product_1.id, "qty": 1}
                ],
            )
            cls.cart = cart
            cls.so = cls.env["sale.order"].browse(info["id"])
            cls.so.payment_mode_id = cls.payment_mode.id

    def test_payment_info(self):
        info = self.cart.dispatch("sync")
        self.assertIn("payment", info)
        self.assertDictEqual(
            {"mode": {"id": self.payment_mode.id, "name": self.payment_mode.name}},
            info["payment"],
        )
