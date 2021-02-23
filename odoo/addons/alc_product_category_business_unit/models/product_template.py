# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"
    business_unit_id = fields.Many2one(
        "product.category",
        string="Business unit",
        compute="_compute_business_unit_id",
        inverse="_inverse_business_unit_id",
        readonly=True,
        store=True,
    )

    @api.depends("product_variant_ids", "product_variant_ids.business_unit_id")
    def _compute_business_unit_id(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.business_unit_id = template.product_variant_ids.business_unit_id

        for template in self - unique_variants:
            template.business_unit_id = False

    def _inverse_business_unit_id(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.business_unit_id = self.business_unit_id
