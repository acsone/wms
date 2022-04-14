# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestOrdersSuiteChannel


class TestOrdersSuiteChannelFlow(TestOrdersSuiteChannel):
    def test_orders_flow(self):
        with self.orders_service() as service:
            result = service.search(page=1, per_page=10)
            self.assertEqual(result["size"], 1)
            self.assertEqual(result["data"][0]["suite_name"], "suite_name")
            self.assertEqual(result["data"][0]["sale_channel"], "phone")

        with self.orders_service() as service:
            result = service.search(page=1, per_page=10, sale_channel="phone")
            self.assertEqual(result["size"], 1)

        with self.orders_service() as service:
            result = service.search(sale_channel="mail")
            self.assertEqual(result["size"], 0)
