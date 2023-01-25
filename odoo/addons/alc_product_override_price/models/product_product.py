# Copyright 2017 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def price_compute(
        self, price_type, uom=None, currency=None, company=None, date=False
    ):
        """Check if context contains a price to return instead of product.

        prices. Otherwise, calls parent method.
        """
        if "override_based_price" in self.env.context:
            return self.env.context.get("override_based_price")
        return super().price_compute(
            price_type, uom=uom, currency=currency, company=company, date=date
        )
