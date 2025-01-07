# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from .common import ProductOnOrderCase


class TestProductOnOrder(ProductOnOrderCase):

    def test_simple_search(self):
        """Check simple call.

        We should have 3 products since we have 3 WIP so
        """
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get("/products_on_order")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 3)

    def test_search_restricts(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"restricts[]": ["is_mto"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get(
                "/products_on_order", params={"restricts[]": ["has_backorder"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

            response = test_client.get(
                "/products_on_order",
                params={"restricts[]": ["has_backorder", "is_mto"]},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

    def test_search_family(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"product_families[]": ["meds"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get(
                "/products_on_order", params={"product_families[]": ["food"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)
            response = test_client.get(
                "/products_on_order", params={"product_families[]": ["meds", "food"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

    def test_search_order_ref(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"order_ref": self.so_medoc_in_stock.name}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

    def test_search_customer_ref(self):
        customer_ref = "my_ref"
        self.so_medoc_in_stock.client_order_ref = customer_ref
        self.so_medoc_in_stock.flush_recordset()
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"customer_ref": customer_ref}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

    def test_search_date_order(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order",
                params={
                    "order_date_min": fields.Datetime.to_datetime(
                        "2020-01-03 13:00:00"
                    ).isoformat(),
                    "order_date_max": fields.Datetime.to_datetime(
                        "2020-01-03 15:00:00"
                    ).isoformat(),
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

    def test_cancel_wrong_ref(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                "/products_on_order/cancel/-1", json={"quantity": 1}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)

    def test_cancel_no_back_order(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_medoc_in_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)

    def test_cancel(self):
        template = self.env.ref(
            "alc_eshop_api_products_on_order.sale_order_request_backorder_cancellation"
        )
        template.auto_delete = False

        all_mails = self.env["mail.mail"].search([])
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_ali_out_of_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], True)
        new_mail = self.env["mail.mail"].search([]) - all_mails
        subject = (
            f"Ref {self.so_ali_out_of_stock.name}: "
            "Demande annulation backorder product_ali"
        )
        self.assertTrue(new_mail)
        self.assertEqual(new_mail.subject, subject)
        self.assertEqual(self.so_ali_out_of_stock.id, new_mail.res_id)
        self.assertEqual(self.so_ali_out_of_stock._name, new_mail.model)

    def test_get(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                f"/products_on_order/{self.so_ali_out_of_stock.order_line.id}"
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()["order_line_id"], self.so_ali_out_of_stock.order_line.id
            )

    def test_get_not_found(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get("/products_on_order/123456789")
            self.assertEqual(response.status_code, 404)
