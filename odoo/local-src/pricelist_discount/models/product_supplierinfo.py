# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp

from odoo import models, fields


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    discount_purchase = fields.Float(
        'Purchase discount (%)',
        digits=dp.get_precision('Discount'),
        default=0.0
    )

    discount_sale = fields.Float(
        'Sale discount (%)',
        digits=dp.get_precision('Discount'),
        default=0.0
    )

    min_qty_sale = fields.Float(
        string='Sale minimal quantity',
        default=0.0,
    )
