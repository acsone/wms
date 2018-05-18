# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import logging

from psycopg2 import IntegrityError
from odoo import fields, models
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'esb.exportable']

    esb_ref = fields.Char(string='Reference for ESB')

    @job(default_channel='root.esb')
    def ws_create_new(self, data):
        """Create a sale order with data coming from webservices."""
        try:
            return self.with_context(
                no_connector_export=True
            )._ws_create_new(data)
        except IntegrityError as error:
            self.env.cr.rollback()
            _logger.error('Webservice create saleorder, integrity error : %s',
                          error)

    def _ws_create_new(self, data):
        order_data = self._ws_create_order_data(data)
        order_data['order_line'] = self._ws_create_order_line_data(data)
        order = self.create(order_data)
        order.action_confirm()
        order.confirmation_date = order.date_order
        return order

    def _ws_create_order_data(self, data):
        order_data = {}
        order_data['team_id'] = self.env.ref(
                'sales_team.salesteam_website_sales').id
        order_data['esb_ref'] = data['increment_id']
        order_data['partner_id'] = data['customer_id']
        order_data['date_order'] = data['date']
        order_data['confirmation_date'] = data['date']
        order_data['client_order_ref'] = data['order_ref']
        order_data['partner_invoice_id'] = data['customer_id']
        order_data['state'] = 'draft'
        if 'carrier_id' in data:
            carrier = self.env['delivery.carrier'].search([
                ('esb_ref', '=', data['carrier_id'])]).exists()
            if len(carrier):
                order_data['carrier_id'] = carrier.id
            else:
                _logger.error('Webservice new saleorder, carrier %s not found',
                              data['carrier_id'])
        return order_data

    def _ws_create_order_line_data(self, data):
        lines = []
        for line in data['lines']:
            if line.get('free'):
                # free line, skip it
                continue
            product = self.env['product.product'].search([
                ('default_code', '=', line['sku'])]).exists()
            if len(product):
                sol = {}
                sol['product_id'] = product.id
                sol['name'] = product.name
                sol['product_uom'] = product.uom_id.id
                sol['product_uom_qty'] = line.pop('quantity')
                sol['price_unit'] = product.list_price
                sol['sequence'] = line.pop('line_id')
                lines.append((0, 0, sol))
            else:
                _logger.error('Webservice new saleorder, product %s not found',
                              line['sku'])
        return lines
