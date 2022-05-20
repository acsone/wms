# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import job


class ProductProduct(models.Model):
    _inherit = "product.product"

    price_cache = fields.Serialized(readonly=True)

    @api.model
    def get_price_cache_products(self, domain=None, domain_extend=None):
        domain = domain or []
        if domain_extend:
            domain += domain_extend
        return self.search(domain)

    @api.model
    def _price_cache_remove_old_items(self, price_cache):
        today = fields.Date.context_today(self)
        item_model = self.env["product.pricelist.item"]
        outdated = lambda x: item_model._is_past_date(x, today)
        pop = [outdated(price_cache[key].get("date_end")) for key in price_cache]
        for key in pop:
            price_cache.pop(key)

    @api.model
    def add_to_cache(self, cache_list, cache_element):
        eid = cache_element["id"]
        cache_list = [e for e in cache_list if e["id"] != eid]
        cache_list.append(cache_element)
        return cache_list

    @api.model
    def remove_from_cache(self, cache_list, element_ids):
        return [e for e in cache_list if e["id"] not in element_ids]

    @job(default_channel="root.background.price")
    def update_price_cache(self, pricelists=None, dates=None, eids=None):
        """If pricelists (or discount_pricelists) is not given,
           it is assumed to mean all pricelists."""
        clean = False  # whether to clean up the cache
        currency = self.env.ref("base.EUR")
        # if we changed the default price of the product, all prices have to be updated
        if not pricelists:
            pricelists = self.env["product.pricelist"].search([])
            clean = True
        dates = dates or {pl.role_name: pl.get_date_witnesses() for pl in pricelists}
        for product in self:
            price_cache = {} if clean else (product.price_cache or {})
            for pricelist in pricelists:
                if not pricelist.is_discount:
                    pl_prices = price_cache.get(pricelist.role_name, [])
                    if eids:
                        pl_prices = self.remove_from_cache(pl_prices, eids)
                    for date in dates[pricelist.role_name]:
                        price = pricelist._get_cache_price(product, date)
                        price["price"] = currency.round(price["price"])
                        pl_prices = self.add_to_cache(pl_prices, price)
                    price_cache[pricelist.role_name] = pl_prices
                else:
                    discount_role = pricelist.discount_role_name
                    pl_discounts = price_cache.get(discount_role, [])
                    if eids:
                        pl_discounts = self.remove_from_cache(pl_discounts, eids)
                    for date in dates[pricelist.role_name]:
                        discount = pricelist._get_cache_discount(product, date)
                        if discount:
                            pl_discounts = self.add_to_cache(pl_discounts, discount)
                    price_cache[discount_role] = pl_discounts

            product.price_cache = price_cache

    @job(default_channel="root.background.price")
    def delay_remove_price_cache(self, pricelist_role_names):
        dsc = _("Remove products prices for pricelist %s.") % pricelist_role_names
        for product in self:
            product.with_delay(description=dsc).remove_price_cache(pricelist_role_names)

    @job(default_channel="root.background.price")
    def remove_price_cache(self, pricelist_role_names):
        # different API: we directly pass the role names so we don't need to access
        # records that have been deleted previously
        for record in self:
            price_cache = record.price_cache or {}
            for pricelist_role_name in pricelist_role_names:
                price_cache.pop(pricelist_role_name, None)
                price_cache.pop("discount_%s" % pricelist_role_name, None)
            record.price_cache = price_cache

    def delay_update_price_cache(self, **kwargs):
        names = ", ".join(self.mapped("name"))
        ns = names if len(names) < 300 else names[: 300 - 5] + "[...]"
        desc = _("Update products prices for product %s.") % ns
        self.with_delay(description=desc).update_price_cache(**kwargs)

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        res.delay_update_price_cache()
        return res

    def write(self, vals):
        watched_fields = [
            "active",
            "list_price",
            "categ_id",
            "price_category_id",
            "price_extra",
        ]
        updated_fields = [f for f in watched_fields if f in vals]
        v = lambda r, f: r[f].id if f in ["categ_id", "price_category_id"] else r[f]
        filter_update = lambda p: any(v(p, f) != vals[f] for f in updated_fields)
        to_update = self.filtered(filter_update)
        res = super(ProductProduct, self).write(vals)
        if to_update:
            to_update.delay_update_price_cache()
        return res

    def _price_cache_get(self, key, date_ref=None):
        self.ensure_one()
        items = self.price_cache.get(key, [])  # TODO: we should not be in that case
        # however, in tests, the matter is different...
        mixin = self.env["mixin.past"]
        date_ref = date_ref or fields.Date.today()
        filter_date = lambda it: (
            not mixin._is_past_date(it["date_end"], date_ref)
            and not mixin._is_future_date(it["date_start"], date_ref)
        )
        candidates = filter(filter_date, items)
        item = {}
        if candidates:
            item = min(candidates, key=lambda it: it["date_start"] or date_ref)
        return item
