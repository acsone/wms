# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from datetime import datetime, timedelta

from odoo.osv.expression import AND
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import falsy2emptystring, falsy2zero

_logger = logging.getLogger(__name__)


class StockUpdateMapper(Component):
    _name = 'esb.stock.update.export.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.product'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and
                    work.timestamp.kind in ['stock.update',
                                            'stock.update.single'])

    direct = [
        (falsy2emptystring('default_code'), 'sku'),
        (falsy2zero('immediately_usable_qty'), 'qty')
    ]

    @mapping
    def compute_erpstockcode(self, record):
        value = ''
        if record.product_tmpl_id.state_id:
            value = record.product_tmpl_id.state_id.esb_ref or ''
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
        return {'sales_average': round(sale_average, 1)}


class StockUpdateExporter(Component):
    """Multiple product stock status exporter, scheduled by cron."""
    _name = 'esb.stock.update.webservice.exporter'
    _inherit = 'esb.webservice.cron.exporter'
    _apply_on = 'product.product'
    _base_backend_adapter_usage = 'backend.adapter.stockupdate'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'stock.update')

    def get_items(self, export_since):
        """Find all quants that need to be exported.

        Returns the quants instead of the products directly because the
        write_date on the quants is used to manage the maximum of records
        that can be sent.
        """
        domain = [
             ('product_id.default_code', '!=', ''),
             ('product_id.default_code', '!=', False),
             ('product_id.type', '=', 'product'),
             ('product_id.sale_ok', '=', True),
             ]
        if export_since:
            date_domain = self.domain_timestamp(export_since)
            domain = AND([domain, date_domain])
        all_quants = self.env['stock.quant'].search(domain)
        return all_quants.sorted(key=lambda r: r.write_date)

    def run(self, export_since=None, max_records=None):
        """ Run the export of multiple stock status.

        ``export_since`` can be omitted to ignore the date and export
        all the records that match the domain.
        ``max_records`` can be set to export only a maximum number of records
        """
        data = []
        exported_ids = []
        exported_until = None
        quants = self.get_items(export_since=export_since)
        for quant in quants:
            if quant.product_id.id not in exported_ids:
                if exported_until and quant.write_date != exported_until:
                    # As the write_date precision is on the second
                    # All quants in the same second must be exported
                    break
                mapped_record = self.mapper.map_record(quant.product_id)
                data.append(self._update_data(mapped_record))
                exported_ids += [quant.product_id.id]
                if max_records != 0 and len(exported_ids) >= max_records:
                    exported_until = quant.write_date
        else:
            exported_until = None
        if data:
            data = {'lines': data}
            self._create(data)
            return exported_until
        return


class StockUpdateServiceExporter(Component):
    """Single product stock status exporter."""
    _name = 'esb.stock.update.webservice.exporter.single'
    _inherit = 'esb.webservice.exporter'
    _apply_on = 'product.product'
    _base_backend_adapter_usage = 'backend.adapter.stockupdate'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and
                    work.timestamp.kind == 'stock.update.single')

    def _get_external_id(self):
        """Always send a POST request, so no external id."""
        return None

    def _postprocess_create_result(self, result):
        return
