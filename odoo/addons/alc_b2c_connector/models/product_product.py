# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.osv import expression

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    @api.model
    def product_assortment_domain(self, endpoint_setting):
        if endpoint_setting.product_assortment_id:
            return endpoint_setting.product_assortment_id._get_eval_domain()
        return []

    def _search_products_from_b2c(
        self, skus: list, limit: int, offset: int, endpoint_setting
    ):
        domain = self.product_assortment_domain(endpoint_setting)
        if skus:
            domain = expression.AND([domain, [("default_code", "in", skus)]])
        products = self.search(domain, limit=limit, offset=offset)
        products.check_access_rights("read")
        return self.search(domain, limit=limit, offset=offset)
