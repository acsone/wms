# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestDiscountService


class TestDiscountServiceFlow(TestDiscountService):
    def test_no_results_if_no_rights(self):
        self.partner.supplier_promotion_sale_allowed = False
        with self.discount_service(self.partner) as service:
            result = service.dispatch("search", params={})
            self.assertEqual(result["size"], 0)

    def test_results_no_past_discount(self):
        with self.discount_service(self.partner) as service:
            result = service.dispatch("search", params={})
            self.assertEqual(result["size"], 2)

    def test_results_search_reference(self):
        with self.discount_service(self.partner) as service:
            result = service.dispatch("search", params={"reference__ilike": "14"})
            self.assertEqual(result["size"], 1)

            result = service.dispatch("search", params={"reference__ilike": "1"})
            self.assertEqual(result["size"], 2)

            result = service.dispatch("search", params={"reference": "1"})
            self.assertEqual(result["size"], 0)

            result = service.dispatch("search", params={"reference": "MDS14"})
            self.assertEqual(result["size"], 1)

            expected = {
                "ratio_main_product": 0,
                "ratio_promotional_product": 0,
                "reference": "MDS14",
                "date_end": self.Date.from_string(self.today_plus(1)),
                "date_start": self.Date.from_string(self.today),
                "discount_sale": 25.0,
                "is_promotion": False,
                "is_sale_discount": True,
            }
            self.assertEqual(result["data"], [expected])
