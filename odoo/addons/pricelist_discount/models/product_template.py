# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def price_compute(
        self, price_type, uom=None, currency=None, company=None, date=False
    ):
        """Check if context contains a price to return instead of product.

        prices. Otherwise, calls parent method.
        """
        try:
            return self.env.context["override_based_price"]
        except KeyError:
            return super().price_compute(
                price_type, uom=uom, currency=currency, company=company, date=date
            )
