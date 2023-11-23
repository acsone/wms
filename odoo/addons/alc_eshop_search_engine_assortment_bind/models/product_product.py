# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    def shopinvader_assortment_binding(self, backend_domain=None):
        self.env["se.backend"].autobind_product_from_assortment(
            domain=backend_domain,
            domain_product=[("id", "in", self.ids)],
        )
