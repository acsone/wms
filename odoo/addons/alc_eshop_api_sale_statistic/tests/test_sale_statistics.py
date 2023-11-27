# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi import status
from freezegun import freeze_time
from requests import Response

from odoo.addons.alc_cerberus_utils import utils

from .common import TestSaleStatistics


class TestSaleStatisticsMonthly(TestSaleStatistics):
    @freeze_time("2020-10-01 00:00:00")
    def test_monthly_ordered(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response: Response = test_client.get(
                f"/sale_statistics/monthly_ordered/{self.product_1.id}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertDictEqual(
                {
                    "average": 4.33,
                    "months": {
                        "2019-10-01": 0.0,
                        "2019-11-01": 0.0,
                        "2019-12-01": 0.0,
                        "2020-01-01": 8.0,
                        "2020-02-01": 4.0,
                        "2020-03-01": 9.0,
                        "2020-04-01": 0.0,
                        "2020-05-01": 0.0,
                        "2020-06-01": 0.0,
                        "2020-07-01": 0.0,
                        "2020-08-01": 0.0,
                        "2020-09-01": 31.0,
                    },
                },
                result,
            )
        with self._create_test_client(partner=self.partner_2) as test_client:
            response: Response = test_client.get(
                f"/sale_statistics/monthly_ordered/{self.product_1.id}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertDictEqual(
                {
                    "average": 0.0,
                    "months": {
                        "2019-10-01": 0.0,
                        "2019-11-01": 0.0,
                        "2019-12-01": 0.0,
                        "2020-01-01": 0.0,
                        "2020-02-01": 0.0,
                        "2020-03-01": 0.0,
                        "2020-04-01": 0.0,
                        "2020-05-01": 0.0,
                        "2020-06-01": 0.0,
                        "2020-07-01": 0.0,
                        "2020-08-01": 0.0,
                        "2020-09-01": 0.0,
                    },
                },
                result,
            )

    @freeze_time("2020-12-03 00:00:00")
    def test_monthly_ordered_not_current_month(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response: Response = test_client.get(
                f"/sale_statistics/monthly_ordered/{self.product_1.id}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
            self.assertDictEqual(
                {
                    "average": 4.33,
                    "months": {
                        "2019-12-01": 0.0,
                        "2020-01-01": 8.0,
                        "2020-02-01": 4.0,
                        "2020-03-01": 9.0,
                        "2020-04-01": 0.0,
                        "2020-05-01": 0.0,
                        "2020-06-01": 0.0,
                        "2020-07-01": 0.0,
                        "2020-08-01": 0.0,
                        "2020-09-01": 31.0,
                        "2020-10-01": 0.0,
                        "2020-11-01": 0.0,
                    },
                },
                result,
            )

    def test_top_ordered(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response: Response = test_client.get("/sale_statistics/top_ordered")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertEqual(2, res["size"])
            self.assertListEqual(
                res["data"],
                [
                    {
                        "product_family": "meds",
                        "date_last_ordered": utils.odoo_dt_to_dt_utc(
                            self.last_date_order
                        )
                        .isoformat()
                        .replace("+00:00", "Z"),
                        "product_id": self.product_2.id,
                        "ordered_count": 12,
                    },
                    {
                        "product_family": "food",
                        "date_last_ordered": utils.odoo_dt_to_dt_utc(
                            self.last_date_order
                        )
                        .isoformat()
                        .replace("+00:00", "Z"),
                        "product_id": self.product_1.id,
                        "ordered_count": 5,
                    },
                ],
            )

    def test_top_ordered_supplier_promotion(self):
        # supplier promotion ends today...
        with self._create_test_client(partner=self.partner_1) as test_client:
            response: Response = test_client.get(
                "/sale_statistics/top_ordered", params={"supplier_discount_only": True}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertTrue(res)
            self.assertEqual(1, res["size"])
            self.assertEqual(1, len(res["data"]))

    def test_top_ordered_limit(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response: Response = test_client.get(
                "/sale_statistics/top_ordered", params={"page": 1, "per_page": 1}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertTrue(res)
            self.assertEqual(2, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_2.id)
            response: Response = test_client.get(
                "/sale_statistics/top_ordered", params={"page": 2, "per_page": 1}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertEqual(2, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_1.id)

    def test_top_ordered_product_family(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response: Response = test_client.get(
                "/sale_statistics/top_ordered", params={"product_families[]": ["meds"]}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertEqual(1, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_2.id)
            response: Response = test_client.get(
                "/sale_statistics/top_ordered",
                params={"product_families[]": ["equipment"]},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertEqual(0, res["size"])
            self.assertEqual(0, len(res["data"]))

    def test_top_ordered_discount_only(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response: Response = test_client.get(
                "/sale_statistics/top_ordered", params={"supplier_discount_only": True}
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertEqual(1, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_1.id)

    def test_five_years(self):
        # no need for freeze time, data is generated relative to now
        with self._create_test_client(partner=self.partner_5y) as test_client:
            response: Response = test_client.get("/sale_statistics/five_years")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            result = response.json()
        self.assertDictEqual(result, {"size": 5, "data": self.expected_5y})
