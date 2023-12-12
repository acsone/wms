# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import pytz

from odoo import api, fields
from odoo.osv.expression import FALSE_LEAF, NEGATIVE_TERM_OPERATORS, OR, TRUE_LEAF

from odoo.addons.mixin_past.models.mixin_past import MixinPast
from odoo.addons.product.models.product_pricelist_item import PricelistItem


class ProductPricelistItem(PricelistItem, MixinPast):
    _name = "product.pricelist.item"

    has_min_quantity = fields.Boolean(
        compute="_compute_has_min_quantity",
        search="_search_has_min_quantity",
        store=False,
    )

    @api.depends("min_quantity")
    def _compute_has_min_quantity(self):
        for record in self:
            record.has_min_quantity = record.min_quantity and record.min_quantity > 1

    @api.model
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

    def _update_price_cache(self, domain_extend=None, dates=None, eids=None):
        domain_extend = domain_extend or []
        eids = (eids or []) + [None]
        for items in self.partition("pricelist_id").values():
            pricelist = items.mapped("pricelist_id")
            pricelist.ensure_one()
            domain = items._get_domains_extend()
            extended_domain = OR([domain, domain_extend or []])
            dates = dates or {}
            dates_pl = pricelist._get_date_witnesses(items=items)
            dates[pricelist.role_name] = set(dates.get(pricelist, [])) | dates_pl
            pricelist._delay_update_price_cache(
                domain_extend=extended_domain, dates=dates, eids=eids
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self._context.get("no_update_price_cache") and not self._context.get(
            "no_update_price_cache_items"
        ):
            records._update_price_cache()
        return records

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
                pl.role_name: pl._get_date_witnesses(pl_items)
                for pl, pl_items in items_by_pricelist.items()
            }
        res = super().write(vals)
        if not update_price_cache:
            return res
        for pricelist, pl_items in items_by_pricelist.items():
            dates_pl = pricelist._get_date_witnesses(pl_items)
            dates = {pricelist.role_name: dates_pl | dates_before[pricelist.role_name]}
            pl_items._update_price_cache(
                domain_extend=extends_before[pricelist], dates=dates, eids=pl_items.ids
            )
        return res

    def unlink(self):
        # it is crucial that these jobs do not get lost,
        # otherwise the id of the item will keep polluting the cache until a full reset.
        # pricelist unlink is the exception, since the parent key gets dropped.
        if not self.env.context.get("no_update_price_cache_items"):
            self._update_price_cache(eids=self.ids)
        return super().unlink()

    def _get_price(self, product, date=None):
        if not date:
            date = fields.Date.context_today(self)
        if self:
            return self._compute_price(
                product, 1, product.uom_id, date, self.currency_id
            )
        return self._compute_base_price(
            product,
            1,
            product.uom_id,
            date,
            product.currency_id,
        )

    def _get_price_base(self, product):
        self.ensure_one()
        return self._compute_base_price(
            product,
            1,
            product.uom_id,
            fields.Date.context_today(self),
            product.currency_id,
        )

    @api.model
    def _datetime_to_date_at_tz(self, dt):
        if not dt:
            return None
        tz = self.env.user.tz or "GMT"
        return dt.astimezone(pytz.timezone(tz)).date()

    @api.model
    def _datetime_to_date_at_tz_iso(self, dt):
        d = self._datetime_to_date_at_tz(dt)
        return d.isoformat() if d else None

    def _cache_price(self, product):
        return {
            "id": self.id or None,  # typed json compatibility
            "price": self._get_price(product, self.date_start),
            "date_start": self._datetime_to_date_at_tz_iso(self.date_start),
            "date_end": self._datetime_to_date_at_tz_iso(self.date_end),
        }

    def _get_product_discount(self, product):
        self.ensure_one()
        if self.compute_price == "percentage":
            alcyon_discount = self.percent_price
        else:
            alcyon_discount = 0
            price = self._get_price_base(product)
            if price:
                discount_price = self._get_price(product)
                alcyon_discount = (price - discount_price) / price * 100
        return alcyon_discount

    def _cache_discount(self, product):
        self.ensure_one()
        alcyon_discount = self._get_product_discount(product)
        cache = {}
        if alcyon_discount:
            cache = {
                "id": self.id,
                "discount": alcyon_discount,
                "date_start": self._datetime_to_date_at_tz_iso(self.date_start),
                "date_end": self._datetime_to_date_at_tz_iso(self.date_end),
            }
            if self.has_min_quantity:
                cache["min_quantity"] = self.min_quantity
        return cache

    def _compute_price(self, product, quantity, uom, date, currency=None):
        currency = currency or self.currency_id
        if not currency:
            currency = self.env.ref("base.EUR")
        return super()._compute_price(product, quantity, uom, date, currency=currency)
