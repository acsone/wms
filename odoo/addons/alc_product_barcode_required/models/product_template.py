# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    no_barcode_authorized = fields.Boolean(
        "Barcode not required for this product",
        related="product_variant_ids.no_barcode_authorized",
    )

    @api.model
    def create(self, vals):
        template = super(
            ProductTemplate, self.with_context(disable_check_barcode_constrains=True)
        ).create(vals)
        related_vals = {}
        if vals.get("no_barcode_authorized"):
            related_vals["no_barcode_authorized"] = vals["no_barcode_authorized"]
        if related_vals:
            template.write(related_vals)
        template.with_context(
            disable_check_barcode_constrains=False
        ).product_variant_ids._check_barcode_is_mandatory()
        return template

    def write(self, vals):
        result = super(
            ProductTemplate, self.with_context(disable_check_barcode_constrains=True)
        ).write(vals)
        for rec in self:
            rec.with_context(
                disable_check_barcode_constrains=False
            ).product_variant_ids._check_barcode_is_mandatory()
        return result
