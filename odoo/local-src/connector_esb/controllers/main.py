# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""

Respond to calls from the ESB.

"""

import logging

from datetime import datetime

import werkzeug

import odoo
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db

_logger = logging.getLogger(__name__)


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
