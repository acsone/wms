# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import logging

from psycopg2 import IntegrityError
from odoo import fields, models
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    esb_ref = fields.Char(string='Reference for ESB')

    @job()
    def ws_create_new(self, data):
        """Create a sale order with data coming from webservices."""
        try:
            return self._ws_create_new(data)
        except IntegrityError as error:
            self.env.cr.rollback()
            _logger.error('Webservice create saleorder, integrity error : %s',
                          error)

    def _ws_create_new(self, data):
        order_data = self._ws_create_order_data(data)
        order_data['order_line'] = self._ws_create_order_line_data(data)
        order = self.create(order_data)
        self._ws_post_create(order, data)
        return order

    def _ws_create_order_data(self, data):
        order_data = {}
        order_data['esb_ref'] = data['increment_id']
        order_data['partner_id'] = data['customer_id']
        order_data['date_order'] = data['date']
        order_data['client_order_ref'] = data['order_ref']
        if 'invoice_address_id' in data:
            order_data['partner_invoice_id'] = data['invoice_address_id']
        if 'shipping_address_id' in data:
            order_data['partner_shipping_id'] = data['shipping_address_id']
        if 'shipping_method' in data:
            order_data['carrier_id'] = data['shipping_method']
        # May not have to be implemented
        order_data['amount_total'] = data['order_amount']
        order_data['amount_tax'] = data['tax_amount']
        order_data['amount_untaxed'] = \
            data['order_amount'] - data['tax_amount']
        order_data['state'] = 'sale'
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

    def _ws_post_create(self, order, data):
        if order.carrier_id:
            # when we have a carrier_id, even with a 0.0 price,
            # Odoo will add a shipping line in the SO when the picking
            # is done, so we better add the line directly
            # even when the price is 0.0.
            order._create_delivery_line(
                order.carrier_id, data.get('shipping_amount', 0.0))
