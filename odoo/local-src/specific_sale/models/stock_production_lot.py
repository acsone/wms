# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.one
    @api.depends('quant_ids.qty')
    def _product_qty(self):
        context = self.env.context or {}
        if context.get('only_wh_stock_quants'):
            self.product_qty = self.product_id.with_context(
                lot_id=self.id
            ).qty_available
        else:
            super(StockProductionLot, self)._product_qty()
