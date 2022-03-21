# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        watched_fields = ["list_price", "categ_id", "price_category_id"]
        updated_fields = [f for f in watched_fields if f in vals]
        v = lambda r, f: r[f].id if f in ["categ_id", "price_category_id"] else r[f]
        filter_update = lambda p: any(v(p, f) != vals[f] for f in updated_fields)
        to_update = self.filtered(filter_update)
        res = super(ProductTemplate, self).write(vals)
        if to_update:
            to_update.mapped("product_variant_ids").delay_update_price_cache()
        return res
