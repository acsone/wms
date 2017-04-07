# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.one
    @api.depends('quant_ids.qty')
    def _product_qty(self):
        context = self.env.context or {}
        if context.get('only_wh_stock_quants'):
            location_ids = self.env.ref('stock.stock_location_stock').ids
            quants = self.env['stock.quant'].search([
                ('lot_id', '=', self.id),
                ('location_id', 'child_of', location_ids)
            ])
            self.product_qty = sum(quants.mapped('qty'))
        else:
            super(StockProductionLot, self)._product_qty()
