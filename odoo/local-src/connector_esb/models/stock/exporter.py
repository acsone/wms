# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class StockExportMapper(Component):
    _name = 'esb.stock.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.product'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'stock')

    direct = [
        ('default_code', 'Sku'),
    ]

    @mapping
    def compute_stock_and_use_date(self, record):
        next_use_date = ''
        total_stock = record.qty_available
        quants = self.env['stock.quant'].search(
                [('product_id', '=', record.id)])
        lots = quants.mapped('lot_id')
        if len(lots):
            lots.sorted(key=lambda r: r.use_date)
            if lots[0].use_date:
                next_use_date = lots[0].use_date.split(' ')[0]
        return {
            'Stock': total_stock,
            # The name of this field is not decided yet...
            'NextUseDate': next_use_date}

    @mapping
    def compute_sales_average(self, record):
        """ Compute the daily average quantity of sale on a year """
        sale_average = 0
        # TODO : waiting for the correct formula to calculate this
        # one_year_back = (datetime.today() -
        #                  timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        # sol = self.env['sale.order.line'].search([
        #     ('product_id', '=', record.id),
        #     ('create_date', '>=', one_year_back)])
        # sale_average = sum(line.product_uom_qty for line in sol) / 365
        return {'SalesAverage': '{0:.3f}'.format(sale_average)}

    @mapping
    def compute_erpstockcode(self, record):
        # The code field in product_state is not implemented yet [ALCN-912]
        # return {'ErpStockCode': record.product_tmpl_id.state_id.code}
        return {'ErpStockCode': ''}


class StockCronExporter(Component):

    _name = 'esb.stock.cron.exporter'
    _inherit = 'esb.cron.exporter'
    _usage = 'record.exporter.cron'
    _apply_on = 'product.product'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'stock')

    def domain_timestamp(self, export_since):
        all_quants = self.env['stock.quant'].search(
            [('write_date', '>', export_since)])
        products = all_quants.mapped('product_id')
        return [('id', 'in', products.ids)]
