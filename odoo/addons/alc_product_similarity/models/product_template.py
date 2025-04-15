# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    similar_products_ids = fields.Json(
        related="product_variant_ids.similar_products_ids"
    )

    @api.model
    def _get_description_vector_recompute_tiggers(self):
        """Returns the fields that will trigger a recompute of the description vector."""
        return {
            "name",
            "description_sale_short",
            "description_sale_long",
        }

    @api.model_create_multi
    def create(self, vals_list):
        # Override to trigger the computation of the description vector
        # when creating a product
        new_products = super().create(vals_list)
        new_products.product_variant_ids._delay_compute_description_vector()
        return new_products

    def write(self, vals):
        # Override to trigger the computation of the description vector
        # when updating a product
        res = super().write(vals)
        triggers = self._get_description_vector_recompute_tiggers()
        if any(field in vals for field in triggers):
            self.product_variant_ids._delay_compute_description_vector()
        return res

