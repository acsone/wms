# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.tools import mute_logger

from odoo.addons.alc_price_cache.tests.common import TestPrices


class TestPricelistItemFlow(TestPrices):
    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.utils")
    def test_no_delay(self):
        # given
        vals = self._get_pricelist_vals("nodelay", [])
        vals["is_discount"] = True
        pricelist = self.model_pl_nodelay.create(vals)

        # given
        vals_item = self._get_item_vals(
            pricelist,
            applied_on="0_product_variant",
            product_id=self.product_1.id,
            exclusive=True,
        )

        # when
        item = self.model_pl_item_nodelay.create(vals_item)

        # then
        price_cache = self.product_1.price_cache[pricelist.discount_role_name]
        expected_price_item = {
            "discount": 10,
            "date_start": None,
            "id": item.id,
            "date_end": None,
            "exclusive": True,
        }
        self.assertEqual(price_cache, [expected_price_item])

        # when
        item.write({"exclusive": False})

        # then
        price_cache = self.product_1.price_cache[pricelist.discount_role_name]
        expected_price_item["exclusive"] = False
        self.assertEqual(price_cache, [expected_price_item])
