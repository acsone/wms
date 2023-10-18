# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_product import ProductProduct as Product
from odoo.addons.product_abc_classification.models.abc_classification_profile import (
    AbcClassificationProfile,
)


class ProductProduct(Product):

    _inherit = "product.product"

    abc_classification_profile_ids = fields.Many2many[AbcClassificationProfile](
        compute="_compute_abc_classification_profile_ids",
        inverse=None,
        store=True,
    )

    @api.depends(
        "product_tmpl_id.package_type_id",
        "product_tmpl_id.is_mto",
        "product_tmpl_id.sale_ok",
    )
    def _compute_abc_classification_profile_ids(self):
        for record in self:
            profiles = record.product_tmpl_id.package_type_id.abc_classification_profile_ids.filtered(
                lambda profile, product=record: not product.is_mto
                or not profile.exclude_product_mto
            )
            profiles = profiles.filtered(
                lambda profile, product=record: product.sale_ok
                or not profile.exclude_non_sellable
            )
            record.abc_classification_profile_ids = profiles
