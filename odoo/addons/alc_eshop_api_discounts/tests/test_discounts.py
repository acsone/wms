# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestDiscountService


class TestDiscountServiceFlow(TestDiscountService):
    def test_no_results_if_no_rights(self):
        self.partner.supplier_promotion_sale_allowed = False
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/discounts")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

    def test_results_no_past_discount(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/discounts", params={"reference": "MDS14"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

    def test_results_search_reference(self):
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/discounts", params={"reference__ilike": "14"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get("/discounts", params={"reference__ilike": "DS"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

            response = test_client.get("/discounts", params={"reference": "1"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

            response = test_client.get("/discounts", params={"reference": "MDS14"})
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result["size"], 1)

            expected = {
                "ratio_main_product": 0,
                "ratio_promotional_product": 0,
                "reference": "MDS14",
                "date_end": self.today_plus(1),
                "date_start": self.today,
                "discount_sale": 25.0,
                "is_promotion": False,
                "is_sale_discount": True,
            }
            self.assertEqual(result["data"], [expected])

    def test_discount_only_veterinary(self):
        self.partner.partner_type = "guest"
        discount = self.discount_food
        params = {"reference": discount.product_tmpl_id.default_code}
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/discounts", params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

        discount.only_for_veterinaries = True
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/discounts", params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 0)

        self.partner.partner_type = "veterinary"
        with self._create_test_client(partner=self.partner) as test_client:
            response = test_client.get("/discounts", params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)
