# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import SUPERUSER_ID, http
from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

_logger = logging.getLogger(__name__)


class StockController(http.Controller):
    @http.route("/connector_esb/stock/product", type="http", auth="user", csrf=False)
    def product_stock_level(self, **kw):
        """ Return stock levels of products

        Expect a POST with multipart/x-www-form-urlencoded
        The stock levels are returned for the SKUs passed in the
        form field ``product[]``::

            $ curl -H "Content-Type: application/x-www-form-urlencoded" \
              -X POST http://localhost/connector_esb/stock/product \
              -d "product[0]=1750132&product[1]=0125732"
              --cookie session_id=xxx

        """
        ensure_db()
        request.uid = SUPERUSER_ID
        env = request.env
        _logger.debug("Calling stock/product with data : %s", request.httprequest.form)

        params = request.httprequest.form.iterlists()
        # Keep only parameters whose key start by product
        skus = [param[1] for param in params if param[0].startswith("product")]
        # Flatten the list of skus and keep only the valid ones
        skus = [sku for sku_grp in skus for sku in sku_grp if sku.isdigit()]
        backend = env["esb.backend"].sudo().get_singleton()
        with backend.work_on("product.product") as work:
            res = work.component("ws.message.product.stock").get_message(skus)
            headers = [("Content-Type", "text/xml")]
            return request.make_response(res, headers)

    @http.route("/connector_esb/stock/cnk", type="json", auth="user", csrf=False)
    def product_stock_cnk(self, products=None):
        """ Return stock levels of all products (use the CNK)
        or for specific products

        Expect a POST with multipart/x-www-form-urlencoded
        The stock levels are returned for all products or for specific
        products if the form field ``products[]`` is filled with CNK::

            $ curl -X POST \
                    http://localhost:8069/connector_esb/stock/cnk"

        """
        ensure_db()
        request.uid = SUPERUSER_ID
        env = request.env

        backend = env["esb.backend"].sudo().get_singleton()
        with backend.work_on("product.product") as work:
            res = work.component("ws.message.product.stock.cnk").get_message(products)
            return res

    @http.route("/connector_esb/stock/sku", type="json", auth="user", csrf=False)
    def product_stock_sku(self, products=None):
        """ Return stock levels of all products (use the SKU)
        or for specific products

        Expect a POST with multipart/x-www-form-urlencoded
        The stock levels are returned for all products or for specific
        products if the form field ``products[]`` is filled with SKU::

            $ curl -X POST \
                    http://localhost:8069/connector_esb/stock/sku"

        """
        ensure_db()
        request.uid = SUPERUSER_ID
        env = request.env

        backend = env["esb.backend"].sudo().get_singleton()
        with backend.work_on("product.product") as work:
            res = work.component("ws.message.product.stock.sku").get_message(products)
            return res
