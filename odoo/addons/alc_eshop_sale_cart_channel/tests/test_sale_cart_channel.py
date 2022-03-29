# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_cart_rest_api.tests.common import TestSaleCartRestApiCase


class TestSaleCartRestApi(TestSaleCartRestApiCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartRestApi, cls).setUpClass()
        with cls.cart_service(cls.partner_1.id) as cart:
            info = cart.sync(
                uuid=None,
                transactions=[
                    {"uuid": "uuid1", "product_id": cls.product_1.id, "qty": 1}
                ],
            )
            cls.cart = cart
            cls.so = cls.env["sale.order"].browse(info["id"])

    def test_channel_in_cart(self):
        self.assertEqual("web", self.so.sale_channel)
        info = self.cart.dispatch("sync")
        self.assertEqual("web", info["channel"])
