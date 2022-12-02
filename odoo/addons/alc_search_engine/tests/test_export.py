# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestExport


class TestExportFlow(TestExport):
    def test_discounts(self):
        values_discount = {
            "date_start": self.tomorrow,
            "date_end": self.tomorrow,
            "discount_sale": 10,
        }
        self.supplierinfo_model.create(self.get_supplierinfo_vals(**values_discount))
        values_promo = {
            "date_start": self.in_two_days,
            "date_end": self.in_two_days,
            "ratio_main_product": 2,
            "ratio_promotional_product": 3,
        }
        self.supplierinfo_model.create(self.get_supplierinfo_vals(**values_promo))

        self.product.update_price_cache()

        # when
        parser = self.export.get_json_parser()
        binding = self.product.shopinvader_bind_ids
        data = binding.jsonify(parser)[0]

        # then
        expected_discounts = [
            dict(
                values_discount, time_frame={"lte": self.tomorrow, "gte": self.tomorrow}
            )
        ]
        self.assertEqual(data["supplier_discount"], expected_discounts)
        expected_promos = [
            dict(
                values_promo,
                time_frame={"lte": self.in_two_days, "gte": self.in_two_days},
            )
        ]
        self.assertEqual(data["supplier_promotion"], expected_promos)
        # ensure price is the price_cache
        self.assertEqual(data["price"]["price-shopinvader-default"][0]["price"], 1)
