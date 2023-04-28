# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.product.models.product_product import ProductProduct as ProductBase


class ProductProduct(ProductBase):
    @api.model
    def get_sku_products_domain(self):
        """Generate the domain to get stock with SKU product."""
        domain = [("sale_ok", "=", True), ("default_code", "!=", False)]

        # The ESB Connector use the user Admin to execute the method
        # However, the real user id is in the context
        current_user = self.env["res.users"].search(
            [("id", "=", self.env.context.get("uid"))]
        )

        if current_user.is_for_olalux:
            domain += self.get_olalux_products_domain()

        return domain
