# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import http
from odoo.exceptions import AccessDenied
from odoo.http import request

from odoo.addons.web.controllers.main import ensure_db

_logger = logging.getLogger(__name__)


class ProductPriceNewpharmaController(http.Controller):
    @http.route("/connector_esb/product/prices", type="http", auth="user", csrf=False)
    def product_stock_level(self, **kw):
        """ Return return product price from new pharma::

            $ curl -H "Content-Type: application/x-www-form-urlencoded" \
              -X POST http://localhost/connector_esb/product/prices \
              --cookie session_id=xxx
        """
        ensure_db()

        if not request.env.user.is_for_newpharma:
            _logger.error(
                "User %s is not a valid user for newpharma",
                request.env.user.display_name,
            )
            raise AccessDenied()
        # The ESB Connector use the user Admin to execute the method
        # However, the real user id is in the context
        data, _ext = (
            request.env["report"]
            .sudo()
            .get_csv(
                request.env.user.partner_id.ids,
                "alc_product_consolidated_price_csv_report",
                {},
            )
        )
        headers = [("Content-Type", "text/csv")]
        return request.make_response(data, headers)
