# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestOrders


class TestOrdersFlow(TestOrders):
    def test_orders_flow(self):
        with self.orders_service() as service:
            params = {"page": 1, "per_page": 10}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["state_label"], "Pending")

            # tolerate missing state
            self.sale_order.shopinvader_state = False
            params = {"page": 1, "per_page": 10}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["data"][0]["state_label"], None)
