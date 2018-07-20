# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import falsy2zero

_logger = logging.getLogger(__name__)


class SaleExportMapper(Component):
    _name = 'esb.sale.order.export.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'sale.order'

    direct = [
        ('id', 'erp_id'),
        (falsy2zero('amount_total'), 'order_amount'),
        (falsy2zero('amount_tax'), 'tax_amount'),
        (falsy2zero('delivery_price'), 'shipping_amount'),
    ]

    children = [('order_line', 'lines', 'sale.order.line')]

    @mapping
    def compute_customer_id(self, record):
        return {'customer_id': record.partner_id.id}

    @mapping
    def compute_date(self, record):
        return {'date': record.date_order[:10]}

    @mapping
    def compute_serial_no(self, record):
        """It's a char field in odoo and web service wants an int"""
        if record.suite_name:
            try:
                value = int(record.suite_name)
            except ValueError:
                return {}
            return {'serial_no': value}
        return {}

    @mapping
    def compute_channel(self, record):
        # Phone channel '01' is the default
        channel = '01'
        if record.sale_channel == 'fax':
            channel = '03'
        elif record.sale_channel == 'mail':
            channel = '08'
        return {'channel': channel}

    @mapping
    def compute_shipping_method(self, record):
        return {'shipping_method': record.carrier_id.esb_ref or
                self.env.ref('__setup__.deliver_carrier_alcyon')
                }

    @mapping
    def compute_order_ref(self, record):
        if record.client_order_ref:
            return {'order_ref': record.client_order_ref or ''}
        return {}

    @mapping
    def compute_status(self, record):
        status = ''
        if record.state == 'cancel':
            status = 'canceled'
        elif record.state in ['draft', 'sale', 'sent', 'confirm_background']:
            status = 'processing'
            partial = record.order_line.filtered(lambda r: r.qty_delivered > 0)
            if len(partial) > 0:
                status = 'partially_shipped'
        elif record == 'done':
            status = 'complete'
        return {'status': status}

    @mapping
    def compute_apb_tax_amount(self, record):
        taxes = record.invoice_ids.mapped(lambda r: r.amount_apb)
        return {'apb_tax_amount': sum(taxes)}

    @mapping
    def compute_increment_id(self, record):
        """ If an esb_ref exists, it is an update, so lets add it """
        if record.esb_ref:
            return {'increment_id': record.esb_ref or ''}


class SaleWebServiceExporter(Component):

    _name = 'esb.sale.order.webservice.exporter'
    _inherit = 'esb.webservice.exporter'
    _apply_on = 'sale.order'
    _base_backend_adapter_usage = 'backend.adapter.saleorder'

    def _get_external_id(self):
        """Return the id for the export

        To implement in subclasses. For instance for a sales order, the
        external id is sale.esb_ref.
        """
        return self.record.esb_ref

    def _postprocess_create_result(self, result):
        """Write locally the ids of the export record

        The response of the ESB webservice should be:

         {"erp_id": "42",
          "increment_id": "1000000348",
          "lines": [
              {"line_number": 10 , "created_id": 106},
              {"line_number": 20 , "created_id": 107},
          ]
         }

        """
        _logger.info('result from HTTP POST request %s', result)
        external_id = result['increment_id']
        self.record.with_context(no_connector_export=True).write({
            'esb_ref': external_id
        })
        # Fix, their web service does not send one line in an array
        lines = result['lines']
        if not isinstance(lines, list):
            lines = [lines]
        for sol in self.record['order_line']:
            line = next((line for line in lines
                        if line['line_number'] == sol.sequence), '')
            if line:
                sol.with_context(no_connector_export=True).write(
                    {'esb_ref': line['created_id']
                     })
