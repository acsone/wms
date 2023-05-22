# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.osv import expression

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    @api.model
    def product_assortment_domain(self, b2c_client):
        if b2c_client.product_assortment_id:
            return b2c_client.product_assortment_id._get_eval_domain()
        return []

    def _search_products_from_b2c(
        self, skus: list, limit: int, offset: int, b2c_client
    ):
        domain = self.product_assortment_domain(b2c_client)
        if skus:
            domain = expression.AND([domain, [("default_code", "in", skus)]])
        return self.search(domain, limit=limit, offset=offset)
