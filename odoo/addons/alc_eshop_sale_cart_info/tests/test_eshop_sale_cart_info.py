# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSaleCartRestApiInfoCase


class TestSaleCartRestApiInfo(TestSaleCartRestApiInfoCase):
    def test_update(self):
        info = self.cart.dispatch(
            "update", params={"customer_ref": "my_ref", "note": "my note"},
        )
        self.assertEqual("my_ref", self.so.client_order_ref)
        self.assertEqual("my note", self.so.note)
        self.assertEqual("my_ref", info["customer_ref"])
        self.assertEqual("my note", info["note"])
