# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    _inherit = "product.product"

    no_barcode_authorized = fields.Boolean(
        compute="_compute_no_barcode_authorized",
        inverse="_inverse_no_barcode_authorized",
    )
    missing_weight = fields.Boolean(default=False, compute="_compute_missing_weight")
    missing_barcode = fields.Boolean(default=False, compute="_compute_missing_barcode")
    template_variant_count = fields.Integer(
        string="Template Variant Count",
        related="product_tmpl_id.product_variant_count",
        readonly=True,
        store=False,
    )

    @api.depends("product_tmpl_id", "product_tmpl_id.no_barcode_authorized")
    def _compute_no_barcode_authorized(self):
        for product in self:
            product.no_barcode_authorized = (
                product.product_tmpl_id.no_barcode_authorized
            )

    def _inverse_no_barcode_authorized(self):
        for product in self:
            template = product.product_tmpl_id
            if template.product_variant_count > 1:
                raise ValidationError(
                    _(
                        "The property 'Barcode Not Required' can only be changed at "
                        "the Product Template level for products with multiple variants."
                    )
                )
            template.no_barcode_authorized = product.no_barcode_authorized

    @api.depends("weight")
    def _compute_missing_weight(self):
        for product in self:
            product.missing_weight = not product.weight

    @api.depends(
        "barcode", "no_barcode_authorized", "product_tmpl_id", "product_tmpl_id.is_new"
    )
    def _compute_missing_barcode(self):
        for product in self:
            product.missing_barcode = (
                not product.product_tmpl_id.is_new
                and not product.barcode
                and not product.no_barcode_authorized
            )

    @api.model_create_multi
    def create(self, vals_list):
        products = super(
            ProductProduct, self.with_context(disable_check_barcode_constrains=True)
        ).create(vals_list)
        if not self.env.context.get("from_template_create"):
            products.product_tmpl_id.with_context(
                disable_check_barcode_constrains=False
            )._check_barcode_is_mandatory()

        # reset context to ensure no side effects
        return products.with_context(disable_check_barcode_constrains=False)

    def write(self, vals):
        res = super().write(vals)

        # When a product.template is created, Odoo implicitly creates a default product.product variant.
        # This product.product variant is then 'written' to (populated) with data.
        # The 'from_template_create' context flag prevents this write from recursively
        # calling the template's constraint too early during that initial process.
        # We thus explicitly call the constraint here to ensure it applies to the product.template
        # only once all relevant fields are updated on its associated product.product variant.
        if not self.env.context.get("from_template_create"):
            self.product_tmpl_id.with_context(
                disable_check_barcode_constrains=False
            )._check_barcode_is_mandatory()
        return res
