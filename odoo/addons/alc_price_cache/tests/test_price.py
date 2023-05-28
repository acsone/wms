# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.fields import Date
from odoo.tools import mute_logger

from .common import TestPrices


class TestPricesFlow(TestPrices):
    @mute_logger("odoo.addons.queue_job.delay")
    def test_create_pricelist(self):
        vals_item_2b = {
            "applied_on": "2b_product_price_category",
            "compute_price": "percentage",
            "percent_price": 5,
            "price_category_id": self.cat_price.id,
        }
        vals_item_3_global = {
            "applied_on": "3_global",
            "compute_price": "percentage",
            "percent_price": 8,
        }
        vals = {
            "name": "Test PL",
            "is_discount": False,
            "item_ids": [(0, 0, vals_item_2b), (0, 0, vals_item_3_global)],
        }
        pricelist = self.model_pl_nodelay.create(vals)

        price_key = pricelist.role_name
        self.assertTrue(price_key in self.product_1.price_cache)

        vals = {
            "name": "Test Discount PL",
            "is_discount": True,
            "item_ids": [(0, 0, vals_item_3_global)],
        }
        discount_pricelist = self.model_pl_nodelay.create(vals)

        discount_key = discount_pricelist.discount_role_name
        self.assertTrue(discount_key in self.product_1.price_cache)

        pricelist.unlink()
        self.assertFalse(price_key in self.product_1.price_cache)
        self.assertTrue(discount_key in self.product_1.price_cache)
        discount_pricelist.unlink()
        self.assertFalse(self.product_1.price_cache)

    @mute_logger("odoo.addons.queue_job.delay")
    def test_pricelist_update(self):
        vals_item_3_global = self._get_item_vals()  # global 10% discount
        vals = self._get_pricelist_vals("T", [vals_item_3_global])
        pricelist = self.model_pl_nodelay.create(vals)

        price_key = pricelist.role_name
        self.assertTrue(self.product_1.price_cache[price_key][0]["price"], 9)

        vals_item_product = self._get_item_vals(
            pricelist=pricelist,
            applied_on="0_product_variant",
            product_id=self.product_1.id,
            percent_price=20,
        )
        item = self.model_pl_item_nodelay.create(vals_item_product)
        self.assertTrue(len(self.product_1.price_cache[price_key]), 1)
        self.assertTrue(self.product_1.price_cache[price_key][0]["price"], 8)
        self.assertTrue(self.product_1.price_cache[price_key][0]["id"], item.id)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_pricelist_date_witnesses_none(self):
        """If there is no timed item, today is a good witness."""
        items = [self._get_item_vals()]
        vals = self._get_pricelist_vals("Date witness 1", items)
        pricelist = self.model_pl_nodelay.create(vals)

        witnesses = pricelist._get_date_witnesses()

        self.assertEqual(witnesses, {Date.from_string("2022-01-01")})

    @mute_logger("odoo.addons.queue_job.delay")
    def test_create_limited_discount_pricelist(self):
        """When we create a discount pricelist, we only recompute necessary items.

        No global item.
        """
        vals_item_1 = {
            "applied_on": "0_product_variant",
            "product_id": self.product_1.id,
            "compute_price": "percentage",
            "percent_price": 5,
        }
        vals = {
            "name": "D",
            "is_discount": True,
            "item_ids": [(0, 0, vals_item_1)],
        }
        pricelist = self.model_pl_nodelay.create(vals)

        price_key = pricelist.discount_role_name
        self.assertTrue(price_key in self.product_1.price_cache)
        self.assertFalse(self.product_2.price_cache)

        # now we add an item on product2; that should work as expected
        vals_item_2 = {
            "pricelist_id": pricelist.id,
            "applied_on": "0_product_variant",
            "product_id": self.product_2.id,
            "compute_price": "percentage",
            "percent_price": 5,
        }
        # when
        item_2 = self.model_pl_item_nodelay.create(vals_item_2)
        # then
        self.assertEqual(self.product_2.price_cache[price_key][0]["id"], item_2.id)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_pricelist_date_witnesses(self):
        """Start should be here, as well as the date after each end."""
        items = [
            self._get_item_vals(date_start="2022-02-03", date_end="2022-02-27"),
            self._get_item_vals(date_start="2022-02-03", date_end="2022-02-15"),
        ]
        vals = self._get_pricelist_vals("Date witness 1", items)
        pricelist = self.model_pl_nodelay.create(vals)

        witnesses = pricelist._get_date_witnesses()

        expected = {"2022-01-01", "2022-02-03", "2022-02-16", "2022-02-28"}
        self.assertSetEqual(witnesses, {Date.from_string(s) for s in expected})
