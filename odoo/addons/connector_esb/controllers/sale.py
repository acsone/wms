# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""

Respond to calls from the ESB.

"""

import logging
from datetime import datetime

import odoo
import werkzeug
from odoo import _, http
from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

_logger = logging.getLogger(__name__)


class SaleController(http.Controller):
    @staticmethod
    def _validate_request(jsonrequest):
        errors = []
        if "params" not in jsonrequest:
            errors.append(_("Required `params` key is missing."))
        if "data" not in jsonrequest.get("params", {}):
            errors.append(_("Required `data` key is missing."))
        if errors:
            raise werkzeug.exceptions.BadRequest("\n".join(errors))

    @staticmethod
    def _validate_create_sale_order(values):
        """Verify order data received through json-rpc"""

        errors = []
        required_keys = ["increment_id", "customer_id", "date", "lines"]
        missing = [k for k in required_keys if k not in values]
        if missing:
            text = _("Required field(s) missing: %s")
            errors.append(text % ", ".join(["`%s`" % x for x in missing]))
        if "lines" in values and not isinstance(values["lines"], list):
            text = _("Field 'lines' must be a <type 'list'> got %s.")
            errors.append(text % type(values["lines"]))
        if errors:
            raise werkzeug.exceptions.BadRequest("\n".join(errors))
        # Check sale date correctness
        sale_date = values["date"]
        try:
            if " " in sale_date:
                datetime.strptime(sale_date, "%Y-%m-%d %H:%M:%S")
            else:
                datetime.strptime(sale_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Invalid sale date %s" % sale_date)
        if errors:
            raise werkzeug.exceptions.BadRequest("\n".join(errors))

    @staticmethod
    def _validate_status_sale_order(values):
        """Verify order data received through json-rpc"""

        errors = []
        required_keys = ["increment_id", "customer_id"]
        missing = [k for k in required_keys if k not in values]
        customer_id = values.get("customer_id", "")
        if missing:
            text = _("Required field(s) missing: %s")
            errors.append(text % ", ".join(["`%s`" % x for x in missing]))
        if not (
            isinstance(customer_id, int)
            or (isinstance(customer_id, basestring) and customer_id.isdigit())
        ):
            text = _("Customer ID must be a number")
            errors.append(text)
        if errors:
            raise werkzeug.exceptions.BadRequest("\n".join(errors))

    @http.route(
        "/connector_esb/sales_order/create", type="json", auth="user", csrf=False
    )
    def create_sale_order(self, **kw):
        """ Create a sale order with data received on request
            (Magento or other customers)

            Expect a POST as json-rpc

            Example to test from bash without auth and with SKU:

            curl -i \
                -H "Content-Type: application/json" \
                -H "Accept:application/json" \
                -X POST http://localhost/connector_esb/sales_order/create \
                -d  @- << EOF
                 {"jsonrpc":"3.0","id":"4321","method":"create", "params":
                 {"data": {
                  "increment_id": "INC-ID",
                  "customer_id":138,
                  "date":"12-7-2017",
                  "order_ref":"refClt",
                  "lines": [
                      {"line_id": 1, "sku": "SER-700200", "quantity": 3}
                   ]
                 }}}
                EOF

            Example to test from bash without auth and with CNK:

            curl -i \
                -H "Content-Type: application/json" \
                -H "Accept:application/json" \
                -X POST http://localhost/connector_esb/sales_order/create \
                -d  @- << EOF
                 {"jsonrpc":"3.0","id":"4321","method":"create", "params":
                 {"data": {
                  "increment_id": "INC-ID",
                  "customer_id":138,
                  "date":"12-7-2017",
                  "order_ref":"refClt",
                  "lines": [
                      {"line_id": 1, "cnk": "SER-700200", "quantity": 3}
                   ]
                 }}}
                EOF
        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        _logger.debug("Calling sales_order/create with data : %s", request.jsonrequest)
        self._validate_request(request.jsonrequest)
        values = request.jsonrequest["params"]["data"]
        self._validate_create_sale_order(values)
        delayable = env["sale.order"].with_delay(priority=2)
        delayable.ws_create_new(values, datetime.now())

    @http.route(
        "/connector_esb/sales_order/status", type="json", auth="user", csrf=False
    )
    def status_sale_order(self, **kw):
        """ Return the status of a sale order

            Expect a POST as json-rpc

            Example to test from bash without auth :

            curl -i \
                -H "Content-Type: application/json" \
                -H "Accept:application/json" \
                -X POST http://localhost/connector_esb/sales_order/status \
                -d  @- << EOF
                 {"jsonrpc":"3.0","id":"4321","method":"create", "params":
                 {"data": {
                  "increment_id": "INC-ID",
                  "customer_id":138,
                 }}}
                EOF

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        _logger.debug("Calling sales_order/status with data : %s", request.jsonrequest)
        self._validate_request(request.jsonrequest)
        values = request.jsonrequest["params"]["data"]
        self._validate_status_sale_order(values)

        partner_ref = values["customer_id"]
        esb_ref = values["increment_id"]

        backend = env["esb.backend"].sudo().get_singleton()
        with backend.work_on("sale.order") as work:
            res = work.component("ws.message.sale.order.status").get_message(
                partner_ref, esb_ref
            )

        return res
