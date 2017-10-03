# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, api, models, _


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    ratio_main_product = fields.Integer('Ratio main product')
    ratio_promotional_product = fields.Integer('Ration free product')
    ratio_display_name = fields.Char('Promotion',
                                     compute='_compute_ratio_display_name',
                                     readonly=True)

    @api.multi
    def _compute_ratio_display_name(self):
        for supplierinfo in self:
            if not supplierinfo.ratio_promotional_product \
                    or not supplierinfo.ratio_main_product:
                continue
            display_name = _('For %s products, %s free') % \
                           (supplierinfo.ratio_main_product,
                            supplierinfo.ratio_promotional_product)
            supplierinfo.ratio_display_name = display_name
