# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""

Respond to calls from the ESB.

"""

import logging

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
        backend = env['esb.backend'].get_singleton()
        with backend.work_on('product.product') as work:
            return work.component('ws.message.product.stock').get_message(skus)
