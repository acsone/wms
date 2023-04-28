# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.product.models.product_product import ProductProduct as ProductBase


class ProductProduct(ProductBase):
    @api.model
    def get_cnk_products_domain(self):
        """Generate the domain to get stock with CNK product."""
        domain = [("sale_ok", "=", True), ("cnk_code", "!=", False)]

        # The web service uses the Admin user to execute the method
        # However, the real user id is in the context
        current_user = self.env["res.users"].search(
            [("id", "=", self.env.context.get("uid"))]
        )

        if current_user.is_for_newpharma:
            domain += self.get_newpharma_products_domain()

        return domain
