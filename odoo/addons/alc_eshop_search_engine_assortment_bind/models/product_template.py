# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    def shopinvader_assortment_binding(self, backend_domain=None):
        products = self.mapped("product_variant_ids")
        products.shopinvader_assortment_binding(backend_domain=backend_domain)
