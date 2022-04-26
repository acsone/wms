# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from odoo.osv.expression import OR


class ProductPricelistItem(models.Model):
    _name = "product.pricelist.item"
    _inherit = ["product.pricelist.item", "mixin.past"]

    pricelist_id = fields.Many2one(
        required=True, readonly=True
    )  # should be in standard

    def _get_product_domain(self):
        self.ensure_one()
        domain = [(1, "=", 1)]  # default: global
        if self.applied_on == "2_product_category":
            domain = [("categ_id", "=", self.categ_id.id)]
        if self.applied_on == "2b_product_price_category":
            domain = [("price_category_id", "=", self.product_price_category.id)]
        if self.applied_on == "1_product":
            domain = [("product_tmpl_id", "=", self.product_tmpl_id.id)]
        if self.applied_on == "0_product_variant":
            domain = [("id", "=", self.product_id.id)]
        return domain

    def _get_domains_extend(self):
        result = []
        for item in self:
            result += item._get_product_domain()
        return result

    def update_price_cache(self, domain_extend=None, dates=None, eids=None):
        domain_extend = domain_extend or []
        for items in self.partition("pricelist_id").values():
            items._update_price_cache(domain_extend, dates, eids=eids)

    def _update_price_cache(self, domain_extend=None, dates=None, eids=None):
        eids = (eids or []) + [None]
        pricelist = self.mapped("pricelist_id")
        pricelist.ensure_one()
        domain = self._get_domains_extend()
        extended_domain = OR([domain, domain_extend or []])
        dates = dates or {}
        dates_pl = pricelist.get_date_witnesses(items=self)
        dates[pricelist.role_name] = set(dates.get(pricelist, [])) | dates_pl
        pricelist.delay_update_price_cache(
            domain_extend=extended_domain, dates=dates, eids=eids
        )

    @api.model
    def create(self, vals):
        res = super(ProductPricelistItem, self).create(vals)
        if not self._context.get("no_update_price_cache") and not self._context.get(
            "no_update_price_cache_items"
        ):
            res.update_price_cache()
        return res

    def write(self, vals):
        # it is possible to change what the item is applied on; therefore it affects
        # what it's domain before the change, as well as after the change.
        items_by_pricelist = self.partition("pricelist_id")
        update_price_cache = not self.env.context.get("no_update_price_cache")
        if update_price_cache:
            extends_before = {
                pl: pl_items._get_domains_extend()
                for pl, pl_items in items_by_pricelist.items()
            }
            dates_before = {
                pl.role_name: pl.get_date_witnesses(pl_items)
                for pl, pl_items in items_by_pricelist.items()
            }
        res = super(ProductPricelistItem, self).write(vals)
        if not update_price_cache:
            return res
        for pricelist, pl_items in items_by_pricelist.items():
            dates_pl = pricelist.get_date_witnesses(pl_items)
            dates = {pricelist.role_name: dates_pl | dates_before[pricelist.role_name]}
            pl_items.update_price_cache(
                domain_extend=extends_before[pricelist], dates=dates, eids=pl_items.ids
            )
        return res

    def unlink(self):
        # it is crucial that these jobs do not get lost,
        # otherwise the id of the item will keep polluting the cache until a full reset.
        # pricelist unlink is the exception, since the parent key gets dropped.
        if not self.env.context.get("no_update_price_cache_items"):
            self.update_price_cache(eids=self.ids)
        return super(ProductPricelistItem, self).unlink()

    def _cache_price(self, product):
        return {
            "id": self.id or None,  # typed json compatibility
            "price": self._get_price(product),
            "date_start": self.date_start or None,
            "date_end": self.date_end or None,
        }

    def _cache_discount(self, product):
        self.ensure_one()
        alcyon_discount = self._get_product_discount(product)
        return (
            {
                "id": self.id,
                "discount": alcyon_discount,
                "date_start": self.date_start or None,
                "date_end": self.date_end or None,
            }
            if alcyon_discount
            else {}
        )

    def _get_product_discount(self, product):
        self.ensure_one()
        if self.compute_price == "percentage":
            alcyon_discount = self.percent_price
        else:
            alcyon_discount = 0
            price = self._get_base_price(product)
            if price:
                discount_price = self._get_price(product)
                alcyon_discount = (price - discount_price) / price * 100
        return alcyon_discount

    def _get_price(self, product):
        # in a pricelist, we can just not find any matching rule
        # in this case, we just get the base_price
        assert len(self) <= 1
        base_price = product.price_compute("list_price")[product.id]
        return self._compute_price(base_price) if self else base_price

    @api.model
    def _get_base_price(self, product):
        return product.price_compute("list_price")[product.id]

    def _compute_price(self, price):
        """Compute the unit price of a product in the context of a pricelist application.
           The unused parameters are there to make the full context available for overrides.
        """
        # taken from odoo#60519: refactoring of price computation in standard
        # this should thus be removed after migrating to 12.0 or above
        # slightly simplified: we don't care about the UoM
        self.ensure_one()
        if self.compute_price == "fixed":
            price = self.fixed_price
        elif self.compute_price == "percentage":
            price = (price - (price * (self.percent_price / 100))) or 0.0
        else:
            # complete formula
            price_limit = price
            price = (price - (price * (self.price_discount / 100))) or 0.0
            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            if self.price_surcharge:
                price_surcharge = self.price_surcharge
                price += price_surcharge

            if self.price_min_margin:
                price_min_margin = self.price_min_margin
                price = max(price, price_limit + price_min_margin)

            if self.price_max_margin:
                price_max_margin = self.price_max_margin
                price = min(price, price_limit + price_max_margin)
        return price
