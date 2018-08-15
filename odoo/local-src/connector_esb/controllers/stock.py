# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db

_logger = logging.getLogger(__name__)


class StockController(http.Controller):

    @http.route('/connector_esb/stock/product',
                type='http', auth='user', csrf=False)
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
        request.uid = SUPERUSER_ID
        env = request.env
        _logger.debug('Calling stock/product with data : %s',
                      request.httprequest.form)
        skus = request.httprequest.form.getlist('product[]')
        skus = [sku.strip() for sku in skus]
        backend = env['esb.backend'].sudo().get_singleton()
        with backend.work_on('product.product') as work:
            res = work.component('ws.message.product.stock').get_message(skus)
            headers = [('Content-Type', 'text/xml')]
            return request.make_response(res, headers)
