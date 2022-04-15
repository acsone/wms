# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestOrders


class TestOrdersFlow(TestOrders):
    def test_orders_flow(self):
        with self.orders_service() as service:
            params = {"page": 1, "per_page": 10}
            result = service.dispatch("search", params=params)
            self.assertEqual(result["size"], 1)
