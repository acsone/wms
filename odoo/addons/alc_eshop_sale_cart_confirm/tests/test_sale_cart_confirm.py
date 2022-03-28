# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_eshop_sale_cart_info.tests.common import (
    TestSaleCartRestApiInfoCase,
)


class TestSaleCartRestApi(TestSaleCartRestApiInfoCase):
    def test_confirm(self):
        info = self.cart.dispatch(
            "confirm",
            params={"uuid": self.so.uuid, "customer_ref": "my_ref", "note": "my note"},
        )
        self.assertEqual("sale", self.so.state)
        self.assertEqual("my_ref", self.so.client_order_ref)
        self.assertEqual("my note", self.so.note)
        self.assertTrue(info)
        state = "processing" if "shopinvader.backend" in self.env else "sale"
        self.assertEqual(state, info["state"])
        self.assertEqual("my_ref", info["customer_ref"])
        self.assertEqual("my note", info["note"])
