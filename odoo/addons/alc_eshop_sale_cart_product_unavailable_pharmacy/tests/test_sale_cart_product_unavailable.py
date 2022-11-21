# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestSaleCartRestApiPharmacy


class TestSaleCartRestApiFlow(TestSaleCartRestApiPharmacy):
    def test_qty_unavailable(self):
        pid = self.product_human.id
        with self.cart_service(self.partner_1.id) as cart_service:
            transaction = {"uuid": "uuid1", "product_id": pid, "qty": 1}
            info = cart_service.sync(uuid=None, transactions=[transaction])
            so = self.env["sale.order"].browse(info["id"])
            self.assertEqual(0, info["lines"][0]["qty_unavailable"])

            transaction = {"uuid": "uuid2", "product_id": pid, "qty": 2}
            info = cart_service.dispatch(
                "sync", params={"uuid": so.uuid, "transactions": [transaction]},
            )

            self.assertEqual(0, info["lines"][0]["qty_unavailable"])

            info = cart_service.dispatch(
                "refresh_qty_unavailable", params={"uuid": so.uuid}
            )
            self.assertEqual(0.0, info["lines"][0]["qty_unavailable"])
            self.assertEqual(0, info["lines"][0]["qty_unavailable_diff"])
