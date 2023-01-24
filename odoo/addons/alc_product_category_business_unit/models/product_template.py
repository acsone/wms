# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_category import ProductCategory
from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    business_unit_id = fields.Many2one[ProductCategory](
        string="Business unit",
        compute="_compute_business_unit_id",
        inverse="_inverse_business_unit_id",
        readonly=True,
        store=True,
    )

    @api.depends("has_one_variant", "product_variant_ids.business_unit_id")
    def _compute_business_unit_id(self):
        unique_variants = self.filtered("has_one_variant")
        for template in unique_variants:
            template.business_unit_id = template.product_variant_ids.business_unit_id
        (self - unique_variants).update({"business_unit_id": False})

    def _inverse_business_unit_id(self):
        if self.has_one_variant:
            self.product_variant_ids.business_unit_id = self.business_unit_id
