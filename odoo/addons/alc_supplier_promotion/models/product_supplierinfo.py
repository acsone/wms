# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _inherit = ["product.supplierinfo", "mixin.past"]

    is_promotion = fields.Boolean(compute="_compute_promotions", store=False)
    is_sale_discount = fields.Boolean(compute="_compute_promotions", store=False)

    @api.depends("discount_sale", "ratio_main_product", "ratio_promotional_product")
    def _compute_promotions(self):
        for record in self:
            record.is_sale_discount = bool(record.discount_sale)
            record.is_promotion = (
                record.ratio_main_product and record.ratio_promotional_product
            )
