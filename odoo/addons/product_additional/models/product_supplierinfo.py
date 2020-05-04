# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    _sql_constraints = [
        (
            "valid_promotion_buyx_gety",
            """CHECK ((ratio_main_product > 0 and ratio_promotional_product > 0) or
               ((ratio_main_product is NULL or ratio_main_product = 0) and
                (ratio_promotional_product is NULL or
                 ratio_promotional_product = 0)))
            """,
            _(
                """A valid promotion on quantity must have both value higher than
                 zero"""
            ),
        )
    ]

    ratio_main_product = fields.Integer("Ratio Main Product")
    ratio_promotional_product = fields.Integer("Ratio Free Product")
    ratio_display_name = fields.Char(
        "Promotion", compute="_compute_ratio_display_name", readonly=True
    )

    @api.multi
    def _compute_ratio_display_name(self):
        for supplierinfo in self:
            if (
                not supplierinfo.ratio_promotional_product
                or not supplierinfo.ratio_main_product
            ):
                continue
            display_name = _("For %s products, %s free") % (
                supplierinfo.ratio_main_product,
                supplierinfo.ratio_promotional_product,
            )
            supplierinfo.ratio_display_name = display_name
