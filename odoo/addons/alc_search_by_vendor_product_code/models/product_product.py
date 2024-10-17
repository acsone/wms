# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api

from odoo.addons.product.models.product_product import ProductProduct as Product


class ProductProduct(Product):
    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """
        When want to be able to search by the vendor product product.

        However we cannot simply modify args by adding the domain
        [('vendor_product_code', '=', name)].

        The solution is to execute the method and look if the number of records
        found is less than the limit. It means that Odoo don't found
        all records. In this case, I search with the vendor_product_code.
        """
        if not args:
            args = []
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        if limit and len(result) >= limit:
            return result
        limit_available = None
        if limit:
            limit_available = limit - len(result)
        existing_ids = [x[0] for x in result]
        products = self.search(
            [
                ("vendor_product_code", "ilike", name),
                ("id", "not in", existing_ids),
                *args,
            ],
            limit=limit_available,
        )
        result += products.name_get()
        return result
