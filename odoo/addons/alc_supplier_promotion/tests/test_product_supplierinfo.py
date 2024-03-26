# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from psycopg2.errors import CheckViolation

from odoo.tools import mute_logger

from .common import TestSupplierInfo


class TestSupplierInfoFlow(TestSupplierInfo):
    def test_discounts(self):
        vals_discount_past = self.get_supplierinfo_vals(
            date_start=self.yesterday, date_end=self.yesterday, discount_sale=9
        )
        discount_past = self.supplierinfo_model.create(vals_discount_past)
        vals_discount_tomorrow = self.get_supplierinfo_vals(
            date_start=self.tomorrow, date_end=self.tomorrow, discount_sale=11
        )
        discount_tomorrow = self.supplierinfo_model.create(vals_discount_tomorrow)

        expected_seller_ids = discount_tomorrow + discount_past
        self.assertEqual(self.product_template.seller_ids, expected_seller_ids)
        self.assertTrue(self.product_template.supplier_discount_ids, discount_tomorrow)

    def test_promos(self):
        vals_promo_past = self.get_supplierinfo_vals(
            date_start=self.yesterday,
            date_end=self.yesterday,
            ratio_promotional_product=4,
            ratio_main_product=5,
        )
        promo_past = self.supplierinfo_model.create(vals_promo_past)
        vals_promo_tomorrow = self.get_supplierinfo_vals(
            date_start=self.tomorrow,
            date_end=self.tomorrow,
            ratio_promotional_product=5,
            ratio_main_product=4,
        )
        promo_tomorrow = self.supplierinfo_model.create(vals_promo_tomorrow)

        expected_seller_ids = promo_tomorrow + promo_past
        self.assertEqual(self.product_template.seller_ids, expected_seller_ids)
        self.assertTrue(self.product_template.supplier_promotion_ids, promo_tomorrow)

    @mute_logger("odoo.sql_db")
    def test_valid_promo(self):
        with self.assertRaises(CheckViolation):
            self.supplierinfo_model.create(
                self.get_supplierinfo_vals(
                    date_start=self.tomorrow,
                    date_end=self.tomorrow,
                    ratio_promotional_product=5,
                    ratio_main_product=-4,
                )
            )
        with self.assertRaises(CheckViolation):
            self.supplierinfo_model.create(
                self.get_supplierinfo_vals(
                    date_start=self.tomorrow,
                    date_end=self.tomorrow,
                    ratio_promotional_product=-5,
                    ratio_main_product=4,
                )
            )
        with self.assertRaises(CheckViolation):
            self.supplierinfo_model.create(
                self.get_supplierinfo_vals(
                    date_start=self.tomorrow,
                    date_end=self.tomorrow,
                    ratio_promotional_product=5,
                    ratio_main_product=0,
                )
            )
        with self.assertRaises(CheckViolation):
            self.supplierinfo_model.create(
                self.get_supplierinfo_vals(
                    date_start=self.tomorrow,
                    date_end=self.tomorrow,
                    ratio_promotional_product=0,
                    ratio_main_product=5,
                )
            )

    def test_ratio_display_name(self):
        supplierinfo = self.supplierinfo_model.create(
            self.get_supplierinfo_vals(
                date_start=self.tomorrow,
                date_end=self.tomorrow,
                ratio_promotional_product=5,
                ratio_main_product=4,
            )
        )
        self.assertEqual(supplierinfo.ratio_display_name, "For 4 products, 5 free")

    def test_promo_json(self):
        vals_promo_tomorrow = self.get_supplierinfo_vals(
            date_start=self.tomorrow,
            date_end=self.tomorrow,
            ratio_promotional_product=5,
            ratio_main_product=4,
        )
        promo_tomorrow = self.supplierinfo_model.create(vals_promo_tomorrow)
        json = self.product_template.supplier_promotion_json
        self.assertEqual(1, len(json))
        expected_json = {
            "ratio_main_product": 4,
            "ratio_promotional_product": 5,
            "date_end": self.tomorrow,
            "date_start": self.tomorrow,
            "time_frame": {"gte": self.tomorrow, "lte": self.tomorrow},
        }
        self.assertDictEqual(json[0], expected_json)
        self.assertFalse(self.product_template.supplier_promotion_json_for_veterinaries)
        promo_tomorrow.only_for_veterinaries = True
        self.assertFalse(self.product_template.supplier_promotion_json)
        json = self.product_template.supplier_promotion_json_for_veterinaries
        self.assertEqual(1, len(json))
        self.assertDictEqual(
            json[0],
            expected_json,
        )

    def test_discount_json(self):
        vals_discount_tomorrow = self.get_supplierinfo_vals(
            date_start=self.tomorrow, date_end=self.tomorrow, discount_sale=11
        )
        discount_tomorrow = self.supplierinfo_model.create(vals_discount_tomorrow)
        json = self.product_template.supplier_discount_json
        self.assertEqual(1, len(json))
        expected_json = {
            "discount_sale": 11,
            "date_end": self.tomorrow,
            "date_start": self.tomorrow,
            "time_frame": {"gte": self.tomorrow, "lte": self.tomorrow},
        }
        self.assertDictEqual(json[0], expected_json)
        self.assertFalse(self.product_template.supplier_discount_json_for_veterinaries)
        discount_tomorrow.only_for_veterinaries = True
        self.assertFalse(self.product_template.supplier_discount_json)
        json = self.product_template.supplier_discount_json_for_veterinaries
        self.assertEqual(1, len(json))
        self.assertDictEqual(json[0], expected_json)
