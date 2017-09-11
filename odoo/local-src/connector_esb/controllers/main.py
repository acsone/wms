# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""

Respond to calls from the ESB.

"""

from datetime import datetime

import werkzeug

import odoo
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db
from odoo.exceptions import UserError


class ESBController(http.Controller):

    @http.route('/connector_esb/stock/product',
                type='http', auth='public', csrf=False)
    def product_stock_level(self, **kw):
        """ Return stock levels of products

        Expect a POST with multipart/form-data.
        The stock levels are returned for the SKUs passed in the
        form field ``product[]``::

            $ curl -X POST \
                    http://localhost:8069/connector_esb/stock/product \
                    -F "product[]=1750132" -F "product[]=0016188"

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        skus = request.httprequest.form.getlist('product[]')
        skus = [sku.strip() for sku in skus]
        backend = env['esb.backend'].sudo().get_singleton()
        with backend.work_on('product.product') as work:
            return work.component('ws.message.product.stock').get_message(skus)

    @http.route('/connector_esb/statistics/form',
                type='http', auth='public', csrf=False)
    def statistics_form(self, **kw):
        """ Return statistics for customers according to filters

        Expect a POST with application/x-www-form-urlencoded.
        Params:
        * customerErpId: partner.ref
        * startDate: format YYYY-mm-dd
        * endDate: format YYYY-mm-dd
        * productType: product family (ALI, MAT, ...)
        * manufacturer: supplier codes of the products (separated by commas)
        * language: FR / EN / NL

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env

        def strptime(value):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise werkzeug.BadRequest('Bad date format, expect YYYY-mm-dd')

        backend = env['esb.backend'].sudo().get_singleton()
        with backend.work_on('res.partner') as work:
            component = work.component('ws.message.statistics.form')
            options = component.options_for_form(
                customer_ref=request.httprequest.form['customerErpId'],
                start=strptime(request.httprequest.form['startDate']),
                end=strptime(request.httprequest.form['endDate']),
                product_type=request.httprequest.form['productType'],
                suppliers=request.httprequest.form['manufacturer'].split(','),
                language=request.httprequest.form['language']
            )
            return component.get_message(options)

    @http.route('/connector_esb/statistics/product/<string:sku>/'
                '<string:customer_ref>', type='http',
                auth='public', csrf=False)
    def product_customer_stat(self, sku, customer_ref):
        """ Return a customer purchase statistics for a specific product for
            the last 12 months

        Expect a GET

        $ curl http://localhost/connector_esb/statistics/product/1322031/464

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        backend = env['esb.backend'].get_singleton()
        with backend.work_on('sale.order.line') as work:
            return (work.component('ws.message.product.customer.stat')
                        .get_message(customer_ref, sku))

    @http.route('/connector_esb/statistics/customer/<string:customer_ref>',
                type='http', auth='public', csrf=False)
    def customer_purchase_statistic(self, customer_ref):
        """ Return a customer 2 years purchase statistics by category

        Expect a GET : connector_esb/statistics/customer/<customer_ref>

            $ curl http://localhost:8069/connector_esb/statistics/customer/469

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        backend = env['esb.backend'].get_singleton()
        with backend.work_on('sale.order.line') as work:
            return (work.component('ws.message.customer.stat')
                    .get_message(customer_ref))

    @staticmethod
    def create_sale_order_check_data(jsonrequest):
        """Verify order data received  through json-rpc"""

        required_keys = ['increment_id', 'customer_id', 'date', 'lines']
        if 'params' not in jsonrequest:
            return _('The params key is missing from request')
        if 'data' not in jsonrequest['params']:
            return _('The data key is missing from request')
        data = jsonrequest['params']['data']

        missing = [k for k in required_keys if k not in data]
        if missing:
            text = _('Required field(s) missing: %s')
            return text % ', '.join(['`%s`' % x for x in missing])
        return ''

    @http.route('/connector_esb/sales_order/create',
                type='json', auth='user', csrf=False)
    def create_sale_order(self, **kw):
        """ Create a sale order with data received on request (Magento)

            Expect a POST as json-rpc

            Example to test from bash without auth :

            curl -i \
                -H "Content-Type: application/json" \
                -H "Accept:application/json" \
                -X POST http://localhost/connector_esb/sales_order/create \
                -d  @- << EOF
                 {"jsonrpc":"3.0","id":"4321","method":"create", "params":
                 {"data": {
                  "increment_id": "INC-ID",
                  "customer_id":138,
                  "invoice_address_id":214,
                  "shipping_address_id": 215,
                  "date":"12-7-2017",
                  "order_ref":"refClt",
                  "order_amount":493,
                  "tax_amount":43,
                  "shipping_amount":21,
                  "lines": [
                      {"line_id": 1, "sku": "SER-700200", "quantity": 3}
                   ]
                 }}}
                EOF

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        error_txt = self.create_sale_order_check_data(request.jsonrequest)
        if error_txt:
            raise UserError(error_txt)
        data = request.jsonrequest['params']['data']
        delayable = env['sale.order'].with_delay()
        delayable.ws_create_new(data)
