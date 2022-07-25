# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import job


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_names(self, limit=300):
        names = ", ".join(self.mapped("name"))
        return names if len(names) < limit else names[: limit - 5] + "[...]"

    def delay_update_price_cache(self, **kwargs):
        if "dates" in kwargs:
            for pl in kwargs["dates"]:
                kwargs["dates"][pl] = list(kwargs["dates"][pl])
        desc = _("Update products prices for pricelist %s.") % self._get_names()
        self.with_delay(description=desc).update_price_cache(**kwargs)

    @job(default_channel="root.background.price")
    def update_price_cache(self, domain_extend=None, dates=None, eids=None):
        domain_extend = domain_extend or []
        product_model = self.env["product.product"]
        products = product_model.get_price_cache_products(domain_extend=domain_extend)
        dates = {k: list(dates[k]) for k in dates} if dates else None
        for product in products:
            product.delay_update_price_cache(pricelists=self, dates=dates, eids=eids)

    def remove_price_cache(self):
        products = self.env["product.product"].get_price_cache_products()
        pl_role_names = self.mapped("role_name")
        desc = _("Remove products prices for pricelist %s.") % self._get_names()
        products.with_delay(description=desc).delay_remove_price_cache(pl_role_names)

    @api.model
    def create(self, vals):
        # if we could batch all item creates in one call, we would not need this.
        # since it is not the case, we want to bypass incremental cache updates
        # to batch everything in one step.
        res = super(
            ProductPricelist, self.with_context(no_update_price_cache_items=True)
        ).create(vals)
        if not self.env.context.get("no_update_price_cache"):
            res.delay_update_price_cache()
        return res

    def _needs_price_cache_recompute(self, vals):
        # in particular, item_ids is NOT a field we care about;
        # the update should go through the item write/create method
        return any(field in vals for field in ["name", "is_discount"])

    def write(self, vals):
        # we don't specifically handle the (in)active case: inactive pricelists
        # can still be on partners, so we need their prices.
        # if we change only the name, we could simply iterate over all products
        # to change the key. But it's very complicated to manage because it depends on
        # context lang, is_discount to know which key, and being careful to get
        # correct old and new names.
        # TODO: changing the name does not call
        #  delay_remove_price_cache(pricelist_role_names)
        #  on all products, so it will only be removed at next full re-computation
        needs_update = self._needs_price_cache_recompute(vals)
        res = super(ProductPricelist, self).write(vals)
        if not self.env.context.get("no_update_price_cache") and needs_update:
            self.delay_update_price_cache()
        return res

    def unlink(self):
        # contrarily to the create case, in the unlink case it is always useful
        # to bypass the cache update on items.
        # If an item is unlinked, we should recompute the price cache;
        # if the pricelist is removed  the cache key should be removed altogether.
        self.remove_price_cache()
        return super(ProductPricelist, self).unlink()

    def get_date_witnesses(self, items=None, date=None):
        """Return the list of all the dates a pricelist should be considered to
           obtain all prices (and can be restricted to a subset of items).
           If there are no date starts/end, will return the date
           (or today, the default for date)
           Date is a parameter mainly to ease testing.
        """
        self.ensure_one()
        items = items or self.item_ids
        date = date or fields.Date.context_today(self)
        current = lambda x: not items._is_past_date(x, date)
        starts = [
            fields.Date.from_string(s)
            for s in items.mapped("date_start")
            if s and current(s)
        ]
        one_day = datetime.timedelta(days=1)
        ends = [
            fields.Date.from_string(e) + one_day
            for e in items.mapped("date_end")
            if e and current(e)
        ]
        return {fields.Date.from_string(date)} | set(starts + ends)

    def _get_cache_discount(self, product, date=False):
        self.ensure_one()
        product.ensure_one()
        date = date or fields.Date.context_today(self)
        rule = self._get_rule(product, date)
        return rule._cache_discount(product) if rule else {}

    def _get_cache_price(self, product, date=False):
        self.ensure_one()
        product.ensure_one()
        date = date or fields.Date.context_today(self)
        rule = self._get_rule(product, date)
        return rule._cache_price(product)
