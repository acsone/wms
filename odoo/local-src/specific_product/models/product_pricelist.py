# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    base = fields.Selection(
        selection_add=[('list_price', 'Sale Price 1')]
    )
