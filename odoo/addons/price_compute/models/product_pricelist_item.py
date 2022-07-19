# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    pricelist_id = fields.Many2one(
        required=True, readonly=True
    )  # should be in standard

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
