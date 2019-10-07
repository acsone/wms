# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    supplier_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        readonly=True,
        related='product_id.supplier_id',
    )
    product_last_in_date = fields.Datetime(
        'Last Purchasing Date', related='product_id.product_last_in_date'
    )
    product_last_out_date = fields.Datetime(
        'Last Selling Date', related='product_id.product_last_out_date'
    )

    def _quants_removal_get_order(self, removal_strategy):
        """ Fixing issue https://github.com/odoo/odoo/issues/31186 """
        if removal_strategy == 'fefo':
            return 'removal_date, in_date, id desc'
        elif removal_strategy == 'fifo':
            return 'in_date, id desc'
        return super(StockQuant, self)._quants_removal_get_order(
            removal_strategy
        )
