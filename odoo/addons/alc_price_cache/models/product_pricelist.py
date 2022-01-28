# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import _, api, fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_names(self, limit=300):
        names = ", ".join(self.mapped("name"))
        return names if len(names) < limit else names[: limit - 5] + "[...]"

    def update_price_cache(self, domain_extend=None, dates=None, eids=None):
        domain_extend = domain_extend or []
        product_model = self.env["product.product"]
        products = product_model.get_price_cache_products(domain_extend=domain_extend)
        desc = _("Update products prices for pricelist %s.") % self._get_names()
        dates = list(dates) if dates else None
        products.with_delay(description=desc).update_price_cache(
            self, dates=dates, eids=eids
        )

    def remove_price_cache(self):
        products = self.env["product.product"].get_price_cache_products()
        pricelist_role_names = self.mapped("role_name")
        desc = _("Remove products prices for pricelist %s.") % self._get_names()
        products.with_delay(description=desc).remove_price_cache(pricelist_role_names)

    @api.model
    def create(self, vals):
        # if we could batch all item creates in one call, we would not need this.
        # since it is not the case, we want to bypass incremental cache updates
        # to batch everything in one step.
        superself = super(ProductPricelist, self.with_context(no_update_cache=True))
        res = superself.create(vals)
        res.update_price_cache()
        return res

    def write(self, vals):
        # we don't specifically handle the (in)active case: inactive pricelists
        # can still be on partners, so we need their prices.
        # TOIMP: we could be more precise and ignore fields like country_ids, etc
        res = super(ProductPricelist, self).write(vals)
        self.update_price_cache()
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

    def _get_rule(self, product, date):
        # this comes basically from _compute_price_rule / Low-level method
        # we don't care about partner or min_qty
        price_categ_id = product.price_category_id.id
        price_category_subquery = "OR item.price_category_id = %(price_categ_id)s"
        price_category_subquery = price_category_subquery if price_categ_id else ""
        query = (
            "SELECT item.id "
            "FROM product_pricelist_item AS item "
            "LEFT JOIN product_category AS categ "
            "ON item.categ_id = categ.id "
            "WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = %(tmpl_id)s)"
            "AND (item.product_id IS NULL OR item.product_id = %(prod_id)s)"
            "AND (item.categ_id IS NULL OR item.categ_id = %(categ_id)s) "
            "AND (item.price_category_id IS NULL" + price_category_subquery + ") "
            "AND (item.pricelist_id = %(self_id)s) "
            "AND (item.date_start IS NULL OR item.date_start<=%(date)s) "
            "AND (item.date_end IS NULL OR item.date_end>=%(date)s)"
            "ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc"
        )
        query_args = {
            "self_id": self.id,
            "tmpl_id": product.product_tmpl_id.id,
            "prod_id": product.id,
            "categ_id": product.categ_id.id,
            "price_categ_id": price_categ_id,  # might be False
            "date": date,
        }
        self._cr.execute(query, query_args)  # pylint: disable=sql-injection
        ids = [x[0] for x in self._cr.fetchall()]
        return self.env["product.pricelist.item"].browse(ids[0] if ids else [])

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
