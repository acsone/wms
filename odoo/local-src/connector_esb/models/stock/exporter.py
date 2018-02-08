# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from datetime import datetime, timedelta

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

_logger = logging.getLogger(__name__)


class StockUpdateMapper(Component):
    _name = 'esb.stock.update.export.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.product'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'stock.update')

    direct = [
        ('default_code', 'sku'),
        ('qty_available', 'qty')
    ]

    @mapping
    def compute_erpstockcode(self, record):
        value = ''
        if record.product_tmpl_id.state_id:
            value = record.product_tmpl_id.state_id.esb_ref
        return {'erp_stock_code': value}

    @mapping
    def compute_date_peremption(self, record):
        value = ''
        lot = self.env['stock.production.lot'].search([
            ('quant_ids.product_id', '=', record.id),
            ('use_date', '!=', False)], order='use_date', limit=1)
        if lot:
            value = lot[0].use_date[:10]
        return {'date_peremption': value}

    @mapping
    def compute_sales_average(self, record):
        """ Compute the daily average quantity of sale on a year """
        one_year_back = (datetime.today() - timedelta(days=365))
        sol = self.env['sale.order.line'].search([
            ('product_id', '=', record.id),
            ('create_date', '>=', one_year_back.strftime("%Y-%m-%d")),
            ('order_id.state', '!=', 'cancel'),
        ])
        sale_average = sum(line.product_uom_qty for line in sol) / 365
        return {'sales_average': '{0:.3f}'.format(sale_average)}


class StockUpdateExporter(Component):
    _name = 'esb.stock.update.webservice.exporter'
    _inherit = 'esb.webservice.cron.exporter'
    _apply_on = 'product.product'
    _base_backend_adapter_usage = 'backend.adapter.stockupdate'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'stock.update')

    def domain_timestamp(self, export_since):
        all_quants = self.env['stock.quant'].search(
            [('write_date', '>', export_since)])
        products = all_quants.mapped('product_id')
        return [('id', 'in', products.ids)]
