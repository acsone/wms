# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""

Respond to calls from the ESB.

"""

import werkzeug

import odoo
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db


class SaleController(http.Controller):

    @staticmethod
    def _validate_request(jsonrequest):
        errors = []
        if 'params' not in jsonrequest:
            errors.append(_('Required `params` key is missing.'))
        if 'data' not in jsonrequest.get('params', {}):
            errors.append(_('Required `data` key is missing.'))
        if errors:
            raise werkzeug.exceptions.BadRequest('\n'.join(errors))

    @staticmethod
    def _validate_create_sale_order(values):
        """Verify order data received through json-rpc"""

        errors = []
        required_keys = ['increment_id', 'customer_id', 'date', 'lines']
        missing = [k for k in required_keys if k not in values]
        if missing:
            text = _('Required field(s) missing: %s')
            errors.append(text % ', '.join(['`%s`' % x for x in missing]))
        if 'lines' in values and not isinstance(values['lines'], list):
            text = _("Field 'lines' must be a <type 'list'> got %s.")
            errors.append(text % type(values['lines']))
        if errors:
            raise werkzeug.exceptions.BadRequest('\n'.join(errors))

    @http.route('/connector_esb/sales_order/create',
                type='json', auth='public', csrf=False)
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
                  "date":"12-7-2017",
                  "order_ref":"refClt",
                  "lines": [
                      {"line_id": 1, "sku": "SER-700200", "quantity": 3}
                   ]
                 }}}
                EOF

        """
        ensure_db()
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        self._validate_request(request.jsonrequest)
        values = request.jsonrequest['params']['data']
        self._validate_create_sale_order(values)
        delayable = env['sale.order'].with_delay()
        delayable.ws_create_new(values)
