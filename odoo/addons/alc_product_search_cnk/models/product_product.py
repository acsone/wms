# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.product.models import product_product


class ProductProduct(product_product.ProductProduct):
    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        if limit and len(result) < limit:
            limit_available = limit - len(result)
            eids = [x[0] for x in result]
            domain = [("cnk_code", "ilike", name), ("id", "not in", eids)] + args
            products = self.search(domain, limit=limit_available)
            result += products.name_get()
        return result
