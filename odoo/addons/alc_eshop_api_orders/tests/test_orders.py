# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestOrdersCase


class TestOrders(TestOrdersCase):
    def test_orders_flow(self):
        with self._create_test_client(partner=self.partner) as test_client:
            params = {"page": 1, "per_page": 10}
            response = test_client.get("/orders", params=params)
            self.assertEqual(200, response.status_code)
            result = response.json()
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["state_label"], "Pending")

            # tolerate missing state
            self.sale_order.shopinvader_state = False
            response = test_client.get("/orders", params=params)
            self.assertEqual(200, response.status_code)
            result = response.json()
            self.assertEqual(result["data"][0]["state_label"], None)
