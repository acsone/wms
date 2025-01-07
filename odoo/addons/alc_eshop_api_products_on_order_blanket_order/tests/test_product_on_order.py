# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_eshop_api_products_on_order.tests.common import ProductOnOrderCase


class TestProductOnOrder(ProductOnOrderCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.blanket_order = cls.sell(
            cls.product_ali, 3, "2020-01-02 14:00:00", confirm=False
        )
        cls.blanket_order.order_type = "blanket"
        cls.blanket_order.blanket_reservation_strategy = "at_call_off"
        cls.blanket_order.write(
            {
                "blanket_validity_start_date": "2020-01-02",
                "blanket_validity_end_date": "2021-01-02",
            }
        )
        cls.blanket_order.action_confirm()

    def test_cancel(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_ali_out_of_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], True)

    def test_cancel_no_back_order(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_medoc_in_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)

    def test_cancel_blanket_order_line_not_allowed(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.blanket_order.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)
