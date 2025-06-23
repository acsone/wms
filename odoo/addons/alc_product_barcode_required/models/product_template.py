# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    no_barcode_authorized = fields.Boolean(
        help="Barcode not required for this product",
        default=lambda self: not self.env["ir.config_parameter"]
        .sudo()
        .get_param("product_barcode_required"),
    )
    missing_barcode = fields.Boolean(default=False, compute="_compute_missing_barcode")

    @api.depends("barcode", "no_barcode_authorized", "package_type_id.is_new")
    def _compute_missing_barcode(self):
        for template in self:
            template.missing_barcode = (
                not template.package_type_id.is_new
                and not template.barcode
                and not template.no_barcode_authorized
            )

    @api.constrains("active", "package_type_id", "barcode", "no_barcode_authorized")
    def _check_barcode_is_mandatory(self):
        if self.env.context.get("disable_check_barcode_constrains"):
            return

        bad_products = self.filtered(
            lambda p: (
                p.active
                and not p.is_new
                and not p.no_barcode_authorized
                and not p.barcode
            )
        )

        if bad_products:
            bad_products_formatted_string = "\n".join(
                [f"* {p.display_name} (id={p.id})" for p in bad_products]
            )
            msg = _(
                "You must enter a barcode or specify product without barcode "
                "for products that are not 'new'.\n"
                "Affected products:\n%s"
            )
            raise ValidationError(msg % bad_products_formatted_string)

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(
            ProductTemplate,
            self.with_context(
                disable_check_barcode_constrains=True, from_template_create=True
            ),
        ).create(vals_list)

        # Only check the constraints for templates alreardy linked to a variant
        # (templates with no variant are templates still not fully created)
        templates.filtered(lambda t: t.product_variant_count > 0).with_context(
            disable_check_barcode_constrains=False
        )._check_barcode_is_mandatory()

        # reset context to ensure no side effects once the template (and product(s)) is fully created
        return templates.with_context(
            disable_check_barcode_constrains=False, from_template_create=False
        )
