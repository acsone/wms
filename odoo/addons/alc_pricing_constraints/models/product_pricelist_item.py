# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.constrains("base", "compute_price")
    def _constrain_no_formula_discount(self):
        if not self.env["product.pricelist"].enforce_discount_constraint():
            return
        if self.filtered(
            lambda r: r.pricelist_id.is_discount and r.compute_price == "formula"
        ):
            # we could be more lenient and allow some simple subcases,
            # but there are no pricing tests in the price_cache at this point
            # so to remove this constraint, tests should be added first.
            raise ValidationError(_("Formula discount items are not supported."))

    @api.constrains(
        "compute_price", "percent_price", "price_surcharge", "price_discount"
    )
    def _constrain_useless_discounts(self):
        if not self.env["product.pricelist"].enforce_discount_constraint():
            return
        filter_bad = lambda r: r.percent_price == 0 and r.compute_price == "percentage"
        if self.filtered(filter_bad):
            raise ValidationError(_("There is a useless (0%) discount."))
        if self.filtered(
            lambda r: r.price_surcharge == 0
            and r.price_discount == 0
            and r.compute_price == "formula"
        ):
            raise ValidationError(_("There is a useless (formula) discount."))

    @api.constrains("base", "compute_price")
    def _constrain_formula_price_base(self):
        if not self.env["product.pricelist"].enforce_discount_constraint():
            return
        filter_bad = lambda r: r.base == "pricelist" and r.compute_price == "formula"
        if self.filtered(filter_bad):
            # we could allow that in the case of base pricelists
            # however we'd have to add tests in the price cache to make sure this
            # is working as intended before doing so.
            message = _("Items based on other pricelists are not supported.")
            raise ValidationError(message)
