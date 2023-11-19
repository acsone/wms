# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.utils import ensure_db

_logger = logging.getLogger(__name__)


class StockController(http.Controller):
    @http.route("/connector_esb/stock/cnk", type="json", auth="user", csrf=False)
    def product_stock_cnk(self, products=None):
        """Return stock levels of all products (use the CNK).

        or for specific products

        Expect a POST with multipart/x-www-form-urlencoded
        The stock levels are returned for all products or for specific
        products if the form field ``products[]`` is filled with CNK::

            $ curl -X POST \
                    http://localhost:8069/connector_esb/stock/cnk"
        """
        ensure_db()
        env = request.env
        ProductProduct = env["product.product"].sudo()

        domain = ProductProduct.get_cnk_products_domain()

        if products:
            domain.append(("cnk_code", "in", products))
            product_recs = ProductProduct.search(domain, order="cnk_code")
        else:
            product_recs = ProductProduct.search(domain, order="cnk_code")

        stock_by_product = product_recs.read(
            ["cnk_code", "immediately_usable_qty", "default_code"]
        )

        result = []
        for line in stock_by_product:
            quantity = line["immediately_usable_qty"]
            quantity = quantity if quantity >= 0 else 0

            result.append(
                {
                    "cnk": line["cnk_code"],
                    "quantity": quantity,
                    "pid": line["default_code"],
                }
            )

        return result

    @http.route("/connector_esb/stock/sku", type="json", auth="user", csrf=False)
    def product_stock_sku(self, products=None):
        """Return stock levels of all products (use the SKU).

        or for specific products

        Expect a POST with multipart/x-www-form-urlencoded
        The stock levels are returned for all products or for specific
        products if the form field ``products[]`` is filled with SKU::

            $ curl -X POST \
                    http://localhost:8069/connector_esb/stock/sku"
        """
        ensure_db()
        env = request.env

        ProductProduct = env["product.product"].sudo()

        domain = ProductProduct.get_sku_products_domain()

        if products:
            domain.append(("default_code", "in", products))
            product_recs = ProductProduct.search(domain, order="default_code")
        else:
            product_recs = ProductProduct.search(domain, order="default_code")

        stock_by_product = product_recs.read(["immediately_usable_qty", "default_code"])

        result = []
        for line in stock_by_product:
            quantity = line["immediately_usable_qty"]
            quantity = quantity if quantity >= 0 else 0

            result.append({"quantity": quantity, "sku": line["default_code"]})

        return result
