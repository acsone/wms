# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.fields import Date
from odoo.tools import mute_logger

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestPrices


class TestPricelistItemFlow(TestPrices):
    """Because of freeze_gun, all jobs have the same created_date; since _order.

    is on created_date DESC, that means recordsets are nondeterministic without
    a call to sort by id.
    """

    @freeze_time("2022-01-01 12:00:00")
    def test_pricelist_item_is_past(self):
        items = [self._get_item_vals()]
        vals = self._get_pricelist_vals("Date witness 1", items)
        with trap_jobs() as trap:
            pricelist = self.model_pl.create(vals)
            trap.assert_enqueued_job(pricelist._update_price_cache)
        item = pricelist.item_ids
        self.assertFalse(item.is_past)
        with trap_jobs() as trap:
            item.date_end = "2021-12-12"
            trap.assert_enqueued_job(
                item.pricelist_id._update_price_cache,
                kwargs={
                    "domain_extend": [(1, "=", 1)],
                    "dates": {pricelist.role_name: [Date.from_string("2022-01-01")]},
                },
            )
        self.assertTrue(item.is_past)
        with trap_jobs() as trap:
            item.date_end = "2022-12-12"
            self.assertSetEqual(
                set(trap.enqueued_jobs[0].kwargs.get("dates").get(pricelist.role_name)),
                {Date.from_string("2022-12-13"), Date.from_string("2022-01-01")},
            )

    @freeze_time("2022-01-01 12:00:00")
    def test_pricelist_item_change_domain(self):
        items = [self._get_item_vals()]
        vals = self._get_pricelist_vals("Domain change", items)
        with trap_jobs() as trap:
            pricelist = self.model_pl.create(vals)
            trap.assert_enqueued_job(pricelist._update_price_cache)
        item = pricelist.item_ids

        expected_domain = [(1, "=", 1)]
        self.assertEqual(item._get_product_domain(), expected_domain)
        with trap_jobs() as trap:
            item.write(
                {"applied_on": "0_product_variant", "product_id": self.product_1.id}
            )
            trap.assert_enqueued_job(
                item.pricelist_id._update_price_cache,
                kwargs={
                    "domain_extend": [(1, "=", 1)],
                    "dates": {pricelist.role_name: [Date.from_string("2022-01-01")]},
                },
            )

        # because the item was global, all products are affected
        # we added an intermediary job...
        # expected_ids = self.env["product.product"].search(expected_domain).ids
        # self.assertEqual(set(last_job.record_ids), set(expected_ids))

        expected_domain = [("id", "=", self.product_1.id)]
        self.assertEqual(item._get_product_domain(), expected_domain)
        with trap_jobs() as trap:
            item.write({"percent_price": 12})
            trap.assert_enqueued_job(
                item.pricelist_id._update_price_cache,
                kwargs={
                    "domain_extend": [
                        "|",
                        ("id", "=", self.product_1.id),
                        ("id", "=", self.product_1.id),
                    ],
                    "dates": {pricelist.role_name: [Date.from_string("2022-01-01")]},
                },
            )

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_no_delay(self):
        # given
        vals = self._get_pricelist_vals("nodelay", [])
        pricelist = self.model_pl_nodelay.create(vals)

        # then: no product specific item
        price_cache = self.product_1.price_cache[pricelist.role_name]
        expected_price_cache = {
            "price": 10,
            "date_start": None,
            "id": None,
            "date_end": None,
        }
        self.assertEqual(price_cache, [expected_price_cache])

        # given
        vals_item = self._get_item_vals(
            pricelist, applied_on="0_product_variant", product_id=self.product_1.id
        )

        # when
        item = self.model_pl_item_nodelay.create(vals_item)

        # then
        price_cache = self.product_1.price_cache[pricelist.role_name]
        expected_price_cache = {
            "price": 9.0,
            "date_start": None,
            "id": item.id,
            "date_end": None,
        }
        self.assertEqual(price_cache, [expected_price_cache])

        # given
        vals_item_write = {"percent_price": 50, "date_start": "2022-02-02"}

        # when
        item.write(vals_item_write)

        # then
        price_cache = self.product_1.price_cache[pricelist.role_name]
        price_cache_sorted = sorted(price_cache, key=lambda x: x["price"])
        expected_price_cache = [
            {
                "price": 5.0,
                "date_start": "2022-02-02",
                "id": item.id,
                "date_end": None,
            },
            {"price": 10.0, "date_start": None, "id": None, "date_end": None},
        ]
        self.assertEqual(price_cache_sorted, expected_price_cache)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_no_delay_price_category(self):
        # given
        vals = self._get_pricelist_vals("nodelay", [])
        pricelist = self.model_pl_nodelay.create(vals)
        self.product_1.price_category_id = self.cat_price

        # then: no product specific item
        price_cache = self.product_1.price_cache[pricelist.role_name]
        expected_price_cache = {
            "price": 10,
            "date_start": None,
            "id": None,
            "date_end": None,
        }
        self.assertEqual(price_cache, [expected_price_cache])

        # given
        vals_item = self._get_item_vals(
            pricelist,
            applied_on="2b_product_price_category",
            price_category_id=self.cat_price.id,
        )

        # when
        item = self.model_pl_item_nodelay.create(vals_item)

        # then
        price_cache = self.product_1.price_cache[pricelist.role_name]
        expected_price_cache = {
            "price": 9.0,
            "date_start": None,
            "id": item.id,
            "date_end": None,
        }
        self.assertEqual(price_cache, [expected_price_cache])
        self.product_1.price_category_id = False
        self.product_1._update_price_cache()
        price_cache = self.product_1.price_cache[pricelist.role_name]
        expected_price_cache = {
            "price": 10,
            "date_start": None,
            "id": None,
            "date_end": None,
        }
        self.assertEqual(price_cache, [expected_price_cache])

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_multiple_discount(self):
        """Check that getting the best discount from the cache matches.

        what is done in the backend (so, in SQL).
        """
        today = "2022-01-01"
        product = self.product_1

        def roles(ps):
            return ps.mapped("discount_role_name")

        vals = self._get_pricelist_vals("DPL1", [], is_discount=True)
        discount_pricelist_1 = self.model_pl_nodelay.create(vals)
        pricelists = discount_pricelist_1
        item_id = product._get_best_applicable_pricelist_item(
            today, quantity=1, pricelists=pricelists, currency=pricelists.currency_id
        )
        cache_item = product._discount_cache_get(roles(pricelists), today)
        self.assertFalse(item_id)
        self.assertEqual(cache_item, None)

        vals_item_global = self._get_item_vals(pricelist=discount_pricelist_1)
        item_global = self.model_pl_item_nodelay.create(vals_item_global)
        item_id = product._get_best_applicable_pricelist_item(
            today, quantity=1, pricelists=pricelists, currency=pricelists.currency_id
        )
        cache_item = product._discount_cache_get(roles(pricelists), today)
        self.assertEqual(item_id, item_global)
        self.assertEqual(cache_item["id"], item_global.id)

        vals = self._get_pricelist_vals("DPL2", [], is_discount=True)
        discount_pricelist_2 = self.model_pl_nodelay.create(vals)
        pricelists |= discount_pricelist_2
        vals_item_fixed = self._get_item_vals(
            pricelist=discount_pricelist_2,
            compute_price="fixed",
            fixed_price=5,  # starting from a 10$ price, that makes a 50% discount
        )
        item_fixed = self.model_pl_item_nodelay.create(vals_item_fixed)
        item_id = product._get_best_applicable_pricelist_item(
            today, quantity=1, pricelists=pricelists, currency=pricelists.currency_id
        )
        cache_item = product._discount_cache_get(roles(pricelists), today)
        self.assertEqual(item_id, item_fixed)
        self.assertEqual(cache_item["id"], item_fixed.id)
        self.assertEqual(cache_item["discount"], 50)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_no_delay_min_qty(self):
        # given
        tmpl = self.product_1.product_tmpl_id
        vals = self._get_pricelist_vals("DPL", [], is_discount=True)
        discount_pricelist = self.model_pl_nodelay.create(vals)
        role = discount_pricelist.discount_role_name
        # at this point, nothing!
        self.assertFalse(self.product_1.price_cache)

        # given
        vals_item_min_qty_2 = self._get_item_vals(
            discount_pricelist,
            min_quantity=2,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        # when
        item_min_qty_2 = self.model_pl_item_nodelay.create(vals_item_min_qty_2)
        # then
        price_cache = self.product_1.price_cache[role]
        expected_cache_element_1 = {
            "discount": 10.0,
            "date_start": None,
            "id": item_min_qty_2.id,
            "date_end": None,
            "min_quantity": 2,
        }
        expected_price_cache = [expected_cache_element_1]
        self.assertEqual(self._remove_extra_keys(price_cache), expected_price_cache)

        # given
        vals_item_no_min = self._get_item_vals(discount_pricelist, percent_price=5)
        # when
        item_no_min = self.model_pl_item_nodelay.create(vals_item_no_min)
        # then
        price_cache = self.product_1.price_cache[role]
        expected_cache_element_2 = {
            "discount": 5.0,
            "date_start": None,
            "id": item_no_min.id,
            "date_end": None,
        }
        expected_price_cache += [expected_cache_element_2]
        # we check set equivalence of dicts, but dicts are unhashable
        self.assertEqual(len(price_cache), len(expected_price_cache))
        self.assertTrue(
            all(x in self._remove_extra_keys(price_cache) for x in expected_price_cache)
        )

        # given
        vals_item_min_qty_20 = self._get_item_vals(
            discount_pricelist,
            percent_price=20,
            min_quantity=20,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        # when
        item_min_qty_20 = self.model_pl_item_nodelay.create(vals_item_min_qty_20)
        # then
        price_cache = self.product_1.price_cache[role]
        expected_cache_element_3 = {
            "discount": 20.0,
            "date_start": None,
            "id": item_min_qty_20.id,
            "date_end": None,
            "min_quantity": 20,
        }
        expected_price_cache += [expected_cache_element_3]
        # we check set equivalence of dicts, but dicts are unhashable
        self.assertEqual(len(price_cache), len(expected_price_cache))
        self.assertTrue(
            all(x in self._remove_extra_keys(price_cache) for x in expected_price_cache)
        )

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_no_delay_write_min_qty_out(self):
        # given
        tmpl = self.product_1.product_tmpl_id
        vals = self._get_pricelist_vals("DPL", [], is_discount=True)
        discount_pricelist = self.model_pl_nodelay.create(vals)
        role = discount_pricelist.discount_role_name
        self.assertFalse(self.product_1.price_cache)

        # given
        vals_item_min_qty = self._get_item_vals(
            discount_pricelist,
            min_quantity=2,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        # when
        item_min_qty = self.model_pl_item_nodelay.create(vals_item_min_qty)
        # then
        price_cache = self.product_1.price_cache[role]
        expected_cache_element = {
            "discount": 10.0,
            "date_start": None,
            "id": item_min_qty.id,
            "date_end": None,
            "min_quantity": 2,
        }
        self.assertEqual(self._remove_extra_keys(price_cache), [expected_cache_element])

        # when: we make it a normal element by removing the minimum quantity
        item_min_qty.write({"min_quantity": 1})
        # then
        price_cache_updated = self.product_1.price_cache[role]
        expected_cache_element.pop("min_quantity")
        self.assertEqual(
            self._remove_extra_keys(price_cache_updated), [expected_cache_element]
        )

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_no_delay_write_min_qty_in(self):
        # given
        tmpl = self.product_1.product_tmpl_id
        vals = self._get_pricelist_vals("DPL", [], is_discount=True)
        discount_pricelist = self.model_pl_nodelay.create(vals)
        role = discount_pricelist.discount_role_name
        self.assertFalse(self.product_1.price_cache)

        # given
        vals_item_min_qty = self._get_item_vals(
            discount_pricelist,
            min_quantity=0,
            applied_on="3_global",
            product_tmpl_id=tmpl.id,
        )
        # when
        item_min_qty = self.model_pl_item_nodelay.create(vals_item_min_qty)
        # then
        price_cache = self.product_1.price_cache[role]
        expected_cache_element = {
            "discount": 10.0,
            "date_start": None,
            "id": item_min_qty.id,
            "date_end": None,
        }
        expected_price_cache = [expected_cache_element]
        self.assertEqual(self._remove_extra_keys(price_cache), expected_price_cache)

        vals = {
            "min_quantity": 5,
            "applied_on": "1_product",
            "product_tmpl_id": tmpl.id,
        }
        item_min_qty.write(vals)

        price_cache_updated = self.product_1.price_cache[role]
        expected_cache_element["min_quantity"] = 5
        self.assertEqual(
            self._remove_extra_keys(price_cache_updated), [expected_cache_element]
        )

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_no_delay_write_min_qtys(self):
        # given
        tmpl = self.product_1.product_tmpl_id
        vals = self._get_pricelist_vals("DPL", [], is_discount=True)
        discount_pricelist = self.model_pl_nodelay.create(vals)
        role = discount_pricelist.discount_role_name
        self.assertFalse(self.product_1.price_cache)

        # given
        vals_item_min_qty_0 = self._get_item_vals(
            discount_pricelist,
            min_quantity=0,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        vals_item_min_qty_1 = self._get_item_vals(
            discount_pricelist,
            percent_price=11,
            min_quantity=1,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        vals_item_min_qty_2 = self._get_item_vals(
            discount_pricelist,
            percent_price=12,
            min_quantity=2,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        # when
        self.model_pl_item_nodelay.create(vals_item_min_qty_0)
        item_min_qty_1 = self.model_pl_item_nodelay.create(vals_item_min_qty_1)
        item_min_qty_2 = self.model_pl_item_nodelay.create(vals_item_min_qty_2)
        # then
        price_cache = self.product_1.price_cache[role]
        expected_cache_element_1 = {
            "discount": 11.0,
            "date_start": None,
            "id": item_min_qty_1.id,
            "date_end": None,
        }
        expected_cache_element_2 = {
            "discount": 12.0,
            "date_start": None,
            "id": item_min_qty_2.id,
            "date_end": None,
            "min_quantity": 2,
        }
        expected_price_cache = [expected_cache_element_1, expected_cache_element_2]
        self.assertEqual(self._remove_extra_keys(price_cache), expected_price_cache)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_no_delay_write_min_qtys_with_dates(self):
        # In this tests we but dates wit min quantities to check that the cache is
        # date are correctly serialized also in this case (BUG after migrating
        # in v16)

        # given
        tmpl = self.product_1.product_tmpl_id
        vals = self._get_pricelist_vals("DPL", [], is_discount=True)
        discount_pricelist = self.model_pl_nodelay.create(vals)
        role = discount_pricelist.discount_role_name
        self.assertFalse(self.product_1.price_cache)

        # given
        vals_item_min_qty_0 = self._get_item_vals(
            discount_pricelist,
            min_quantity=0,
            percent_price=11,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        vals_item_min_qty_1 = self._get_item_vals(
            discount_pricelist,
            percent_price=12,
            min_quantity=3,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
            date_start="2022-01-01",
            date_end="2022-01-03",
        )
        item_min_qty_0 = self.model_pl_item_nodelay.create(vals_item_min_qty_0)
        item_min_qty_1 = self.model_pl_item_nodelay.create(vals_item_min_qty_1)
        price_cache = self.product_1.price_cache[role]
        expected_cache_element_0 = {
            "discount": 11.0,
            "date_start": None,
            "id": item_min_qty_0.id,
            "date_end": None,
        }
        expected_cache_element_1 = {
            "discount": 12.0,
            "date_start": "2022-01-01",
            "id": item_min_qty_1.id,
            "date_end": "2022-01-03",
            "min_quantity": 3.0,
        }
        expected_price_cache = [expected_cache_element_0, expected_cache_element_1]
        self.assertEqual(self._remove_extra_keys(price_cache), expected_price_cache)

    @mute_logger("odoo.addons.queue_job.delay")
    def test_multi_discount_same_qty_same_date_different_priority(self):
        """You can specify multiple rules with the same min_quantity that will.

        be valid at the same date. Nevertheless, for this date, you should keep
        only the rule with the highest priority (fixed by the order by applied_on)
        for each min_quantity.
        """
        vals = self._get_pricelist_vals("DPL", [], is_discount=True)
        discount_pricelist = self.model_pl_nodelay.create(vals)
        role = discount_pricelist.discount_role_name
        tmpl = self.product_1.product_tmpl_id
        # declare global rule that applies to all products a discount of 5%
        vals_item_min_qty = self._get_item_vals(
            discount_pricelist,
            min_quantity=0,
            percent_price=5,
            applied_on="3_global",
        )
        item_min_qty = self.model_pl_item_nodelay.create(vals_item_min_qty)
        price_cache = self.product_1.price_cache[role]
        expected_cache_element = {
            "discount": 5.0,
            "date_start": None,
            "id": item_min_qty.id,
            "date_end": None,
        }
        self.assertEqual(self._remove_extra_keys(price_cache), [expected_cache_element])

        # declare specific product rule to reset the discount for this product
        vals_item_min_qty_0 = self._get_item_vals(
            discount_pricelist,
            min_quantity=0,
            percent_price=0,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        self.model_pl_item_nodelay.create(vals_item_min_qty_0)
        price_cache = self.product_1.price_cache[role]
        self.assertEqual(self._remove_extra_keys(price_cache), [])

        # introduce a specific rule for product_1 with a discount of 11% only
        # for a min_quantity of 2
        vals_item_min_qty_2 = self._get_item_vals(
            discount_pricelist,
            min_quantity=2,
            percent_price=11,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        item_min_qty_2 = self.model_pl_item_nodelay.create(vals_item_min_qty_2)

        # For product_1, we have 2 rules with min_quantity = 0 and 1 rule with min_quantity = 2
        # into the cache we should have only 1 rule with min_quantity = 2
        # Indeed the rule vals_item_min_qty_0 will disable the rule vals_item_min_qty
        # since it has a higher priority. Therefore, this product we only have
        # a discount of 11% for a min_quantity of 2
        price_cache = self.product_1.price_cache[role]
        expected_cache_element = {
            "discount": 11.0,
            "date_start": None,
            "id": item_min_qty_2.id,
            "date_end": None,
            "min_quantity": 2.0,
        }
        self.assertEqual(self._remove_extra_keys(price_cache), [expected_cache_element])
