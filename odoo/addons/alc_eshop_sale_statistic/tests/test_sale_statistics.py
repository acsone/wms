# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.addons.alc_cerberus_utils import utils

from .common import TestSaleStatistics


class TestSaleStatisticsMonthly(TestSaleStatistics):
    @freeze_time("2020-10-01 00:00:00")
    def test_monthly_ordered(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.monthly_ordered(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 4.333,
                    "months": {
                        "2019-10-01": 0,
                        "2019-11-01": 0,
                        "2019-12-01": 0,
                        "2020-01-01": 8.0,
                        "2020-02-01": 4.0,
                        "2020-03-01": 9.0,
                        "2020-04-01": 0,
                        "2020-05-01": 0,
                        "2020-06-01": 0,
                        "2020-07-01": 0,
                        "2020-08-01": 0,
                        "2020-09-01": 31.0,
                    },
                },
                result,
            )
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_2.id
        ) as service:
            result = service.monthly_ordered(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 0,
                    "months": {
                        "2019-10-01": 0,
                        "2019-11-01": 0,
                        "2019-12-01": 0,
                        "2020-01-01": 0,
                        "2020-02-01": 0,
                        "2020-03-01": 0,
                        "2020-04-01": 0,
                        "2020-05-01": 0,
                        "2020-06-01": 0,
                        "2020-07-01": 0,
                        "2020-08-01": 0,
                        "2020-09-01": 0,
                    },
                },
                result,
            )

    @freeze_time("2020-12-03 00:00:00")
    def test_monthly_ordered_not_current_month(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.monthly_ordered(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 4.333,
                    "months": {
                        "2019-12-01": 0,
                        "2020-01-01": 8.0,
                        "2020-02-01": 4.0,
                        "2020-03-01": 9.0,
                        "2020-04-01": 0,
                        "2020-05-01": 0,
                        "2020-06-01": 0,
                        "2020-07-01": 0,
                        "2020-08-01": 0,
                        "2020-09-01": 31.0,
                        "2020-10-01": 0,
                        "2020-11-01": 0,
                    },
                },
                result,
            )

    def test_top_ordered(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered()
            self.assertTrue(res)
            self.assertEqual(2, res["size"])
            self.assertListEqual(
                res["data"],
                [
                    {
                        "product_family": "meds",
                        "date_last_ordered": utils.odoo_str_dt_to_dt_utc(
                            self.last_date_order
                        ),
                        "product_id": self.product_2.id,
                        "ordered_count": 12.0,
                    },
                    {
                        "product_family": "food",
                        "date_last_ordered": utils.odoo_str_dt_to_dt_utc(
                            self.last_date_order
                        ),
                        "product_id": self.product_1.id,
                        "ordered_count": 5.0,
                    },
                ],
            )

    def test_top_ordered_limit(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered(page=1, per_page=1)
            self.assertTrue(res)
            self.assertEqual(2, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_2.id)
            res = service.top_ordered(page=2, per_page=1)
            self.assertEqual(2, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_1.id)

    def test_top_ordered_product_family(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered(product_families=["meds"])
            self.assertEqual(1, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_2.id)
            res = service.top_ordered(product_families=["equipment"])
            self.assertEqual(0, res["size"])
            self.assertEqual(0, len(res["data"]))

    def test_top_ordered_discount_only(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered(supplier_discount_only=True)
            self.assertEqual(0, res["size"])
            self.assertEqual(0, len(res["data"]))
