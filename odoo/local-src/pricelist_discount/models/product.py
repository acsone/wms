# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def price_compute(self,
                      price_type, uom=False,
                      currency=False, company=False):
        """ Check if context contains a price to return instead of product
        prices. Otherwise calls parent method.
        """
        try:
            return self.env.context['override_based_price']
        except KeyError:
            return super(ProductProduct, self).price_compute(
                price_type=price_type, uom=uom,
                currency=currency, company=company
            )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def price_compute(self,
                      price_type, uom=False,
                      currency=False, company=False):
        """ Check if context contains a price to return instead of product
        prices. Otherwise calls parent method.
        """
        try:
            return self.env.context['override_based_price']
        except KeyError:
            return super(ProductTemplate, self).price_compute(
                price_type=price_type, uom=uom,
                currency=currency, company=company
            )
