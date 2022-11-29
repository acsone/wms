# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv.expression import FALSE_LEAF, NEGATIVE_TERM_OPERATORS, OR, TRUE_LEAF


class ProductPricelistItem(models.Model):
    _name = "product.pricelist.item"
    _inherit = ["product.pricelist.item", "mixin.past"]

    has_min_quantity = fields.Boolean(
        compute="_compute_has_min_quantity",
        search="_search_has_min_quantity",
        store=False,
    )

    @api.depends("min_quantity")
    def _compute_has_min_quantity(self):
        for record in self:
            record.has_min_quantity = record.min_quantity and record.min_quantity > 1

    def _search_has_min_quantity(self, operator, value):
        negative_op = operator in NEGATIVE_TERM_OPERATORS
        domain = []
        has_min_quantity = (not value and negative_op) or (value and not negative_op)
        if "in" in operator:  # value should be a list
            if not value:
                domain = TRUE_LEAF if negative_op else FALSE_LEAF
            elif True in value and False in value:
                domain = FALSE_LEAF if negative_op else TRUE_LEAF
            elif False in value:  # not in [False]
                has_min_quantity = negative_op
            else:  # in [True]
                has_min_quantity = not negative_op
        result_operator = ">=" if has_min_quantity else "<"
        return domain or [("min_quantity", result_operator, 2)]

    def _get_product_domain(self):
        self.ensure_one()
        domain = [(1, "=", 1)]  # default: global
        if self.applied_on == "2_product_category":
            domain = [("categ_id", "=", self.categ_id.id)]
        if self.applied_on == "2b_product_price_category":
            domain = [("price_category_id", "=", self.price_category_id.id)]
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
        # its domain before the change, as well as after the change.
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
        cache = {}
        if alcyon_discount:
            cache = {
                "id": self.id,
                "discount": alcyon_discount,
                "date_start": self.date_start or None,
                "date_end": self.date_end or None,
            }
            if self.has_min_quantity:
                cache["min_quantity"] = self.min_quantity
        return cache
