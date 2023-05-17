# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductProduct(ProductTemplateBase):
    has_no_dimensions = fields.Boolean(
        default=False,
        compute="_compute_has_no_dimensions",
        store=True,
        index=True,
    )

    packaging_has_no_dimensions = fields.Boolean(
        default=False,
        compute="_compute_packaging_has_no_dimensions",
        store=True,
        index=True,
    )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.product_height",
        "product_variant_ids.product_length",
        "product_variant_ids.product_width",
    )
    def _compute_has_no_dimensions(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for product in unique_variants:
            if product.type == "service":
                # No dimensions on services
                continue
            product.has_no_dimensions = not (
                product.product_length
                or product.product_width
                or product.product_height
            )

        for product in self - unique_variants:
            product.has_no_dimensions = False

    @api.depends(
        "packaging_ids",
        "packaging_ids.height",
        "packaging_ids.packaging_length",
        "packaging_ids.width",
    )
    def _compute_packaging_has_no_dimensions(self):
        for product in self:
            if product.type == "service":
                # No dimensions on services
                continue

            packagings = product.mapped("packaging_ids")
            if packagings:
                missing_dimensions = []
                for pack in packagings:
                    if not (pack.packaging_length or pack.width or pack.height):
                        missing_dimensions.append(True)
                    else:
                        missing_dimensions.append(False)
                if any(missing_dimensions):
                    product.packaging_has_no_dimensions = True
                else:
                    product.packaging_has_no_dimensions = False
            else:
                product.packaging_has_no_dimensions = False
