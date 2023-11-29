# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import _, api, fields
from odoo.osv.expression import OR

from odoo.addons.product.models.product_pricelist import Pricelist


class ProductPricelist(Pricelist):
    def _get_names(self, limit=300):
        names = ", ".join(self.mapped("name"))
        return names if len(names) < limit else names[: limit - 5] + "[...]"

    def _delay_update_price_cache(self, **kwargs):
        if "dates" in kwargs:
            for pl in kwargs["dates"]:
                kwargs["dates"][pl] = list(kwargs["dates"][pl])
        desc = _("Update products prices for pricelist {pricelist}.").format(
            pricelist=self._get_names()
        )
        self.with_delay(description=desc)._update_price_cache(**kwargs)

    def _update_price_cache(self, domain_extend=None, dates=None, eids=None):
        domain_extend = domain_extend or []
        product_model = self.env["product.product"]
        products = product_model._get_price_cache_products(domain_extend=domain_extend)
        dates = {k: list(dates[k]) for k in dates} if dates else None
        for product in products:
            product._delay_update_price_cache(pricelists=self, dates=dates, eids=eids)

    def _remove_price_cache(self):
        products = self.env["product.product"]._get_price_cache_products()
        pl_role_names = self.mapped("role_name")
        desc = _("Remove products prices for pricelist {names}.").format(
            names=self._get_names()
        )
        products.with_delay(description=desc)._delay_remove_price_cache(pl_role_names)

    @api.model_create_multi
    def create(self, vals_list):
        # if we could batch all item creates in one call, we would not need this.
        # since it is not the case, we want to bypass incremental cache updates
        # to batch everything in one step.
        records = super(
            ProductPricelist, self.with_context(no_update_price_cache_items=True)
        ).create(vals_list)
        if self.env.context.get("no_update_price_cache"):
            return records
        for rec in records:
            if rec.is_discount:
                domains = [i._get_product_domain() for i in rec.mapped("item_ids")]
                if domains:
                    rec._delay_update_price_cache(domain_extend=OR(domains))
            else:
                rec._delay_update_price_cache()
        return records

    @api.model
    def _price_cache_recompute_depends_fields(self):
        return ["name", "is_discount"]

    @api.model
    def _needs_price_cache_recompute(self, vals):
        # in particular, item_ids is NOT a field we care about;
        # the update should go through the item write/create method
        return any(
            field in vals for field in self._price_cache_recompute_depends_fields()
        )

    def write(self, vals):
        # we don't specifically handle the (in)active case: inactive pricelists
        # can still be on partners, so we need their prices.
        # if we change only the name, we could simply iterate over all products
        # to change the key. But it's very complicated to manage because it depends on
        # context lang, is_discount to know which key, and being careful to get
        # correct old and new names.
        # TODO: changing the name does not call
        #  _delay_remove_price_cache(pricelist_role_names)
        #  on all products, so it will only be removed at next full re-computation
        needs_update = self._needs_price_cache_recompute(vals)
        res = super().write(vals)
        if not self.env.context.get("no_update_price_cache") and needs_update:
            self._delay_update_price_cache()
        return res

    def unlink(self):
        # contrarily to the create case, in the unlink case it is always useful
        # to bypass the cache update on items.
        # If an item is unlinked, we should recompute the price cache;
        # if the pricelist is removed  the cache key should be removed altogether.
        self._remove_price_cache()
        return super().unlink()

    def _get_date_witnesses(self, items=None, date=None):
        """Return the list of all the dates a pricelist should be considered to.

        obtain all prices (and can be restricted to a subset of items).
        If there are no date starts/end, will return the date
        (or today, the default for date)
        Date is a parameter mainly to ease testing.
        """

        def _current(pricelist_items, date_start, ref_date):
            return not pricelist_items._is_past_date(date_start, ref_date)

        self.ensure_one()
        items = items or self.item_ids
        if isinstance(date, datetime.datetime):
            date = date.date()
        date = date or fields.Date.context_today(self)
        starts = [
            date_start.date()
            for date_start in items.mapped("date_start")
            if date_start and _current(items, date_start, date)
        ]
        one_day_delta = datetime.timedelta(days=1)
        ends = [
            date_end.date() + one_day_delta
            for date_end in items.mapped("date_end")
            if date_end and _current(items, date_end, date)
        ]
        return {date} | set(starts + ends)

    def _get_cache_discounts(self, product, date=False):
        self.ensure_one()
        product.ensure_one()
        date = date or fields.Date.context_today(self)
        res = []
        for rule in self._get_applicable_rules(product, date):
            cache = rule._cache_discount(product)
            if cache:
                res.append(cache)
        return res

    def _get_cache_price(self, product, date=False):
        self.ensure_one()
        product.ensure_one()
        date = date or fields.Date.context_today(self)
        rules = self._get_applicable_rules(product, date)
        if rules:
            return [rule._cache_price(product) for rule in rules]
        return [rules._cache_price(product)]
