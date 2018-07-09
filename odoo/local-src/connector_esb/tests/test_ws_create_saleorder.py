# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.addons.connector_esb.controllers.sale import SaleController
from odoo.exceptions import MissingError
from werkzeug.exceptions import BadRequest


class WSCreateSaleOrderTestCase(TransactionCase):

    def setUp(self):
        super(WSCreateSaleOrderTestCase, self).setUp()
        self.controller = SaleController()
        self.fiji = self.env.ref('base.fj')
        self.fiji.esb_ref = 'fj'
        self.setup_records()
        self.order_data = {
            "increment_id": "INC-ID",
            "customer_id": self.partner.ref,
            "date": "2017-09-18",
            "order_ref": "refClt",
            "lines": [{
                'line_id': '1',
                'sku': '0001',
                'quantity': 3,
                'free': False,
            }, {
                # free line: to be skipped
                'line_id': '2',
                'sku': 'FOO',
                'quantity': 3,
                'free': True,
            }, ]
        }
        self.request_data = {
            "jsonrpc": "3.0", "id": "4321",
            "method": "create",
            "params": {
                "data": self.order_data
            }
        }

    def setup_records(self):
        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'default_code': '0001',
            'list_price': 10.0,
        })
        self.partner = self.env['res.partner'].create(
            {'name': 'John Doe',
             'ref': '111111',
             }
        )
        self.partner_shipping = self.env['res.partner'].create({
            'name': 'John Doe (ship)',
            'type': 'delivery',
            'street': 'Middle street 2',
            'city': 'Some Island',
            'zip': '7492125',
            'country_id': self.fiji.id,
            'parent_id': self.partner.id,
        })

    def test_create_saleorder(self):
        starting_date = fields.Datetime().now()
        order = self.env['sale.order']._ws_create_new(self.order_data)
        tax_rate = self.p1.taxes_id.amount / 100.0
        expected = {
            'esb_ref': 'INC-ID',
            'client_order_ref': 'refClt',
            'partner_id': self.partner,
            'partner_invoice_id': self.partner,
            'partner_shipping_id': self.partner_shipping,
            'amount_total': self.p1.list_price * 3 * (1 + tax_rate),
            'amount_tax': self.p1.list_price * 3 * tax_rate,
        }
        for k, v in expected.iteritems():
            if isinstance(v, float):
                self.assertAlmostEqual(order[k], v)
            else:
                self.assertEqual(order[k], v)
        # free line: to be skipped
        self.assertEqual(len(order.order_line), 1)
        # Confirmtation/order date are the time of creation in Odoo by the ws
        self.assertTrue(starting_date <= order.confirmation_date <=
                        fields.Datetime.now())
        self.assertTrue(starting_date <= order.date_order <=
                        fields.Datetime.now())

    def test_create_saleorder_shipping(self):
        carrier = self.env['delivery.carrier'].search([], limit=1)
        carrier.esb_ref = '95'
        data = self.order_data.copy()
        data['carrier_id'] = carrier.esb_ref
        order = self.env['sale.order']._ws_create_new(data)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.carrier_id, carrier)

    def test_request_data(self):
        """ Check for well formed data and some compulsory fields """
        data = self.request_data.copy()
        data.pop('params')
        with self.assertRaises(BadRequest):
            self.controller._validate_request(data)

    def test_required_fields_1(self):
        data = self.request_data.copy()
        data['params']['data'].pop('increment_id')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_2(self):
        data = self.request_data.copy()
        data['params']['data'].pop('customer_id')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_3(self):
        data = self.request_data.copy()
        data['params']['data'].pop('date')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_4(self):
        data = self.request_data.copy()
        data['params']['data'].pop('lines')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_5(self):
        """Check lines is a list"""
        data = self.request_data.copy()
        data['params']['data']['lines'] = data['params']['data']['lines'][0]
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_integrity_error(self):
        data = self.order_data.copy()
        # set inexisting partner
        data['customer_id'] = 999999
        # internal api will raise IntegrityError
        with self.assertRaises(MissingError):
            self.env['sale.order']._ws_create_new(data)

    def test_draft_invoice_is_not_exported(self):
        """Check that invoices in state draft are not exported."""
        data = {
            'esb_ref': 'ref_01',
            'partner_id': self.partner.id,
            'date_order': '2018-01-29',
            'sale_channel': 'fax',
            'state': 'draft',
            'order_line': [
                (0, 0, {
                    'sequence': 1,
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom_qty': 7,
                })],
        }
        # Could not get to patch esb_export_record, so doing it differentely
        # with patch('odoo.addons.connector_esb.models.esb_exportable.'
        #            'ESBExportable.esb_export_record') as export_record:
        with patch('odoo.addons.queue_job.job.DelayableRecordset.__init__',
                   return_value=None) as export_record:
            self.env['sale.order'].create(data)
            export_record.assert_not_called()
