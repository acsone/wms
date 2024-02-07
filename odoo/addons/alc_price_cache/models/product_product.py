# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):

    price_cache = fields.Json(readonly=True, prefetch=False)

    @api.model
    def _get_price_cache_products(self, domain=None, domain_extend=None):
        domain = domain or []
        if domain_extend:
            domain += domain_extend
        return self.search(domain)

    @api.model
    def _price_cache_remove_old_items(self, price_cache):
        item_model = self.env["product.pricelist.item"]
        today = fields.Date.context_today(self)

        def _outdated(x):
            return item_model._is_past_date(x, today)

        pop = [_outdated(price_cache[key].get("date_end")) for key in price_cache]
        for key in pop:
            price_cache.pop(key)

    @api.model
    def _add_to_cache(self, cache_list, cache_element):
        """Filters outdated element when adding a new item to the cache.

        An element is outdated if it has the same id (which means we modified the item)
        or the item operates on the same date range.
        An example of the latter is that we added a new, more precise item.
        So, there was a date-free price on the category, but we added a product-specific
        item. The category item might still be relevant for other products.
        """
        eid = cache_element.get("id")
        ds, de = cache_element.get("date_start"), cache_element.get("date_end")
        min_quantity = cache_element.get("min_quantity", 1)
        cache_element.update({"date_start": ds, "date_end": de})
        res = []
        added = False
        for element in cache_list:
            if element["id"] != eid and (
                element["date_start"] != ds
                or element["date_end"] != de
                or min_quantity != element.get("min_quantity", 1)
            ):
                res.append(element)
            elif (
                element["id"]
                and eid
                and element["id"] > eid
                and element["date_start"] == ds
                and element["date_end"] == de
            ):
                res.append(element)
                added = True
        if not added:
            res.append(cache_element)
        return res

    @api.model
    def _remove_from_cache(self, cache_list, element_ids):
        return [e for e in cache_list if e["id"] not in element_ids]

    def _get_price_cache(self, pricelists, dates, clean=False):
        self.ensure_one()
        price_cache = {} if clean else (self.price_cache or {})
        for pricelist in pricelists:
            if not pricelist.is_discount:
                pl_prices = []
                for date in dates[pricelist.role_name]:
                    cache_prices = pricelist._get_cache_price(self, date)
                    for cache_price in cache_prices:
                        cache_price["price"] = self.currency_id.round(
                            cache_price["price"]
                        )
                        pl_prices = self._add_to_cache(pl_prices, cache_price)
                price_cache[pricelist.role_name] = pl_prices
            else:
                discount_role = pricelist.discount_role_name
                pl_discounts = []
                for date in dates[pricelist.role_name]:
                    discounts = pricelist._get_cache_discounts(self, date)
                    for discount in discounts:
                        pl_discounts = self._add_to_cache(pl_discounts, discount)
                        pl_discounts = self._update_pricelist_cache_min_quantities(
                            pricelist, pl_discounts
                        )
                price_cache[discount_role] = pl_discounts
        return price_cache

    def _update_price_cache(self, pricelists=None, dates=None):
        """If pricelists (or discount_pricelists) is not given,.

        it is assumed to mean all pricelists.
        """
        clean = False  # whether to clean up the cache
        # if we changed the default price of the product, all prices have to be updated
        if not pricelists:
            pricelists = self.env["product.pricelist"].search([])
            clean = True
        dates = dates or {pl.role_name: pl._get_date_witnesses() for pl in pricelists}
        for product in self:
            product.price_cache = product._get_price_cache(pricelists, dates, clean)

    def _update_pricelist_cache_min_quantities(self, pricelist, price_cache):
        # Simpler algorithm: we remove and start anew for all min_qty items
        # we could have a "refresh_min_qty" parameter passed through items, pricelists,
        # and products; however it seems it would not be worth the complexity,
        # especially given all cases that would have to be considered.
        # For most products, it only adds 1 query to find no such items and that's it.
        cleaned_cache = [it for it in price_cache if (it.get("min_quantity") or 1) < 2]
        min_qty_items = self._get_min_qty_items(pricelist)
        cache_min_qty_items = [item._cache_discount(self) for item in min_qty_items]
        return cleaned_cache + cache_min_qty_items

    def _get_min_qty_items(self, pricelist):
        self.ensure_one()
        domain = [
            ("pricelist_id", "=", pricelist.id),
            ("product_tmpl_id", "=", self.product_tmpl_id.id),
            ("applied_on", "=", "1_product"),
            ("has_min_quantity", "=", True),
            ("is_past", "=", False),
        ]
        return self.env["product.pricelist.item"].search(domain)

    def _delay_remove_price_cache(self, pricelist_role_names):
        dsc = _("Remove products prices for pricelist {names}.").format(
            names=pricelist_role_names
        )
        for product in self:
            product.with_delay(description=dsc)._remove_price_cache(
                pricelist_role_names
            )

    def _remove_price_cache(self, pricelist_role_names):
        # different API: we directly pass the role names so we don't need to access
        # records that have been deleted previously
        for record in self:
            price_cache = record.price_cache or {}
            for pricelist_role_name in pricelist_role_names:
                price_cache.pop(pricelist_role_name, None)
                price_cache.pop(f"discount_{pricelist_role_name}", None)
            record.price_cache = price_cache

    def _delay_update_price_cache(self, **kwargs):
        names = ", ".join(self.mapped("name"))
        ns = names if len(names) < 300 else names[: 300 - 5] + "[...]"
        desc = _("Update products prices for product {names}").format(names=ns)
        self.with_delay(description=desc, priority=50)._update_price_cache(**kwargs)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("no_update_price_cache"):
            records._delay_update_price_cache()
        return records

    def write(self, vals):
        def _value(rec, field):
            return (
                rec[field].id
                if field in ["categ_id", "price_category_id"]
                else rec[field]
            )

        watched_fields = [
            "active",
            "list_price",
            "standard_price",
            "categ_id",
            "price_category_id",
            "price_extra",
        ]
        updated_fields = [f for f in watched_fields if f in vals]
        to_update = self.filtered(
            lambda product: any(
                _value(product, field) != vals[field] for field in updated_fields
            )
        )
        res = super().write(vals)
        if to_update and not self.env.context.get("no_update_price_cache"):
            to_update._delay_update_price_cache()
        return res

    def _price_cache_get(self, key, date_ref=None):
        self.ensure_one()
        return self._resolve_price_cache_get(self.price_cache, key, date_ref=date_ref)

    @api.model
    def _resolve_price_cache_get(self, price_cache, key, date_ref=None):
        if not price_cache:
            return {}
        items = price_cache.get(key, [])  # TODO: we should not be in that case
        # however, in tests, the matter is different...
        mixin = self.env["mixin.past"]
        date_ref = date_ref or fields.Date.today()
        candidates = list(
            filter(
                lambda it: (
                    not mixin._is_past_date(it["date_end"], date_ref)
                    and not mixin._is_future_date(it["date_start"], date_ref)
                ),
                items,
            )
        )
        item = {}
        if candidates:
            item = min(candidates, key=lambda it: it["date_start"] or date_ref)
        return item

    def _discount_cache_get(self, discount_keys, date_ref=None):
        self.ensure_one()
        cache = self.price_cache
        return self._resolve_discount_cache_get(cache, discount_keys, date_ref)

    @api.model
    def _resolve_discount_cache_get(self, price_cache, discount_keys, date_ref=None):
        def _filter_date(item):
            return not mixin._is_past_date(
                item["date_end"], date_ref
            ) and not mixin._is_future_date(item["date_start"], date_ref)

        if not price_cache:
            return None

        date_ref = date_ref or fields.Date.today()

        mixin = self.env["mixin.past"]
        caches = [price_cache.get(key, []) for key in discount_keys]
        candidates = [item for cache in caches for item in cache if _filter_date(item)]
        return max(candidates, key=lambda x: x["discount"]) if candidates else None

    @api.model
    def _resolve_discount_cache(self, price_cache, discount_keys):
        item = self._resolve_discount_cache_get(price_cache, discount_keys)
        return item["discount"] if item else 0
