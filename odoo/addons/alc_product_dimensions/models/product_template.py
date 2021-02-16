# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    length = fields.Float(
        compute="_compute_pt_length", inverse="_inverse_pp_length", store=False
    )
    height = fields.Float(
        compute="_compute_pt_height", inverse="_inverse_pp_height", store=False
    )
    width = fields.Float(
        compute="_compute_pt_width", inverse="_inverse_pp_width", store=False
    )
    weight = fields.Float(
        compute="_compute_pt_weight", inverse="_inverse_pp_weight", store=False
    )
    volume_liter = fields.Float(
        related="product_variant_ids.volume_liter", readonly=True
    )
    dimensional_uom_id = fields.Many2one(
        related="product_variant_ids.dimensional_uom_id",
        default=lambda d: d.env.ref("product.product_uom_cm").id,
        readonly=True,
    )

    @api.model
    def create(self, vals):
        template = super(ProductTemplate, self).create(vals)

        related_vals = {}
        if vals.get("length"):
            related_vals["length"] = vals["length"]
        if vals.get("height"):
            related_vals["height"] = vals["height"]
        if vals.get("width"):
            related_vals["width"] = vals["width"]
        if related_vals:
            template.write(related_vals)
        return template

    @api.depends("product_variant_ids", "product_variant_ids.length")
    def _compute_pt_length(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.length = template.product_variant_ids.length

        for template in self - unique_variants:
            template.length = 0.0

    def _inverse_pp_length(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.length = self.length

    @api.depends("product_variant_ids", "product_variant_ids.width")
    def _compute_pt_width(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.width = template.product_variant_ids.width
        for template in self - unique_variants:
            template.width = 0.0

    def _inverse_pp_width(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.width = self.width

    @api.depends("product_variant_ids", "product_variant_ids.height")
    def _compute_pt_height(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.height = template.product_variant_ids.height
        for template in self - unique_variants:
            template.height = 0.0

    def _inverse_pp_height(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.height = self.height

    @api.depends("product_variant_ids", "product_variant_ids.weight")
    def _compute_pt_weight(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.weight = template.product_variant_ids.weight
        for template in self - unique_variants:
            template.weight = 0.0

    def _inverse_pp_weight(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.weight = self.weight
