# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_packaging import ProductPackaging
from odoo.addons.product.models.product_template import ProductTemplate as TemplateBase


class ProductTemplate(TemplateBase):

    packaging_ids = fields.One2many[ProductPackaging](
        search="_search_product_packaging_ids"
    )

    @api.model
    def _search_product_packaging_ids(self, operator, value):
        return [
            ("has_one_variant", "=", True),
            ("product_variant_ids.packaging_ids", operator, value),
        ]
