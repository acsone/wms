# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    no_barcode_authorized = fields.Boolean(
        "Barcode not required for this product",
        related="product_variant_ids.no_barcode_authorized",
        readonly=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(
            ProductTemplate, self.with_context(disable_check_barcode_constrains=True)
        ).create(vals_list)
        for template, vals in zip(templates, vals_list, strict=True):
            related_vals = {}
            if vals.get("no_barcode_authorized"):
                related_vals["no_barcode_authorized"] = vals["no_barcode_authorized"]
            if related_vals:
                template.write(related_vals)
        templates.with_context(
            disable_check_barcode_constrains=False
        ).product_variant_ids._check_barcode_is_mandatory()
        return templates

    def write(self, vals):
        result = super(
            ProductTemplate, self.with_context(disable_check_barcode_constrains=True)
        ).write(vals)
        for rec in self:
            rec.with_context(
                disable_check_barcode_constrains=False
            ).product_variant_ids._check_barcode_is_mandatory()
        return result
