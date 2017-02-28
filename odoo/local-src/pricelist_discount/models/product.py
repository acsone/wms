# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _price_get(self, cr, uid, products, ptype='list_price', context=None):
        """ Check if context contains a price to return instead of product
        prices. Otherwise calls parent method.
        """
        try:
            return context['override_based_price']
        except KeyError:
            return super(ProductTemplate, self)._price_get(
                cr, uid, products, ptype=ptype, context=context
            )
