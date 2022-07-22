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
