# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.addons.alc_eshop_sale_cart_info.tests.common import (
    TestSaleCartRestApiInfoCase,
)


class TestSaleCartRestApi(TestSaleCartRestApiInfoCase):
    def test_confirm(self):
        date_order = "2020-01-01 20:00:00"
        self.so.date_order = date_order
        self.assertEqual(date_order, self.so.date_order)
        confirm_date = "2021-01-01 07:10:00"
        with freeze_time(confirm_date):
            info = self.cart.dispatch(
                "confirm",
                params={
                    "uuid": self.so.uuid,
                    "customer_ref": "my_ref",
                    "note": "my note",
                },
            )

        self.assertEqual("sale", self.so.state)
        self.assertEqual("my_ref", self.so.client_order_ref)
        self.assertEqual("my note", self.so.note)
        self.assertTrue(info)
        state = "processing" if "shopinvader.backend" in self.env else "sale"
        self.assertEqual(state, info["state"])
        self.assertEqual("my_ref", info["customer_ref"])
        self.assertEqual("my note", info["note"])
        self.assertEqual(confirm_date, self.so.date_order)
