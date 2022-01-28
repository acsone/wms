# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.fields import Date

from .common import TestPrices


class TestPricelistItemFlow(TestPrices):
    """Because of freeze_gun, all jobs have the same created_date; since _order
       is on created_date DESC, that means recordsets are nondeterministic without
       a call to sort by id.
    """

    @freeze_time("2022-01-01 12:00:00")
    def test_pricelist_item_is_past(self):
        job_counter = self.job_counter()
        items = [self._get_item_vals()]
        vals = self._get_pricelist_vals("Date witness 1", items)
        pricelist = self.model_pl.create(vals)
        item = pricelist.item_ids
        queue_job = job_counter.search_created()
        self.assertEqual(len(queue_job), 1)

        self.assertFalse(item.is_past)

        item.date_end = "2021-12-12"

        self.assertTrue(item.is_past)
        queue_job = job_counter.search_created()
        self.assertEqual(len(queue_job), 2)
        expected = {Date.from_string("2022-1-1")}
        last_job = max(queue_job, key=lambda x: x.id)
        self.assertEqual(set(last_job.kwargs["dates"]), expected)

        item.date_end = "2022-12-12"

        self.assertFalse(item.is_past)
        queue_job = job_counter.search_created()
        last_job = max(queue_job, key=lambda x: x.id)
        self.assertEqual(len(queue_job), 3)
        expected = {Date.from_string(s) for s in ("2022-1-1", "2022-12-13")}
        self.assertEqual(set(last_job.kwargs["dates"]), expected)

    def test_pricelist_item_change_domain(self):
        job_counter = self.job_counter()
        items = [self._get_item_vals()]
        vals = self._get_pricelist_vals("Domain change", items)
        pricelist = self.model_pl.create(vals)
        item = pricelist.item_ids
        queue_job = job_counter.search_created()
        self.assertEqual(len(queue_job), 1)

        expected_domain = [(1, "=", 1)]
        self.assertEqual(item._get_product_domain(), expected_domain)

        item.write({"applied_on": "0_product_variant", "product_id": self.product_1.id})

        queue_job = job_counter.search_created()
        last_job = max(queue_job, key=lambda x: x.id)
        self.assertEqual(len(queue_job), 2)
        # because the item was global, all products are affected
        expected_ids = self.env["product.product"].search(expected_domain).ids
        self.assertEqual(set(last_job.record_ids), set(expected_ids))

        expected_domain = [("id", "=", self.product_1.id)]
        self.assertEqual(item._get_product_domain(), expected_domain)

        item.write({"percent_price": 12})

        queue_job = job_counter.search_created()
        last_job = max(queue_job, key=lambda x: x.id)
        self.assertEqual(len(queue_job), 3)
        # the item was already restricted to one product
        self.assertEqual(last_job.record_ids, self.product_1.ids)
