# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.addons.connector_esb.controllers.sale import SaleController
from psycopg2 import IntegrityError
from werkzeug.exceptions import BadRequest


class WSCreateSaleOrderTestCase(TransactionCase):

    def setUp(self):
        super(WSCreateSaleOrderTestCase, self).setUp()
        self.controller = SaleController()
        self.setup_records()
        self.order_data = {
            "increment_id": "INC-ID",
            "customer_id": self.partner.id,
            "invoice_address_id": self.partner.id,
            "shipping_address_id": self.partner_shipping.id,
            "date": "2017-09-18",
            "order_ref": "refClt",
            "order_amount": 493,
            "tax_amount": 43,
            "shipping_amount": 21,
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
        self.partner = self.env['res.partner'].create({'name': 'John Doe'})
        self.partner_shipping = self.env['res.partner'].create({
            'name': 'John Doe (ship)',
            'type': 'delivery',
            'parent_id': self.partner.id,
        })

    def test_create_saleorder(self):
        order = self.env['sale.order']._ws_create_new(self.order_data)
        tax_rate = self.p1.taxes_id.amount / 100.0
        expected = {
            'esb_ref': 'INC-ID',
            'client_order_ref': 'refClt',
            'date_order': '2017-09-18 00:00:00',
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

    def test_create_saleorder_shipping(self):
        carrier = self.env['delivery.carrier'].search([], limit=1)
        data = self.order_data.copy()
        data['shipping_amount'] = 10.0
        data['shipping_method'] = carrier.id
        order = self.env['sale.order']._ws_create_new(data)
        self.assertEqual(len(order.order_line), 2)
        shipping_line = order.order_line.filtered(
            lambda x: x.product_id == carrier.product_id)
        self.assertTrue(shipping_line)
        self.assertEqual(shipping_line.price_unit, 10.0)

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

    def test_integrity_error(self):
        data = self.order_data.copy()
        # set inexisting partner
        data['shipping_address_id'] = 999999
        # internal api will raise IntegrityError
        with self.assertRaises(IntegrityError):
            self.env['sale.order']._ws_create_new(data)

    def test_integrity_error_just_log(self):
        """ Data not correct, no exception but log added """
        data = self.order_data.copy()
        # set inexisting partner
        data['shipping_address_id'] = 999999
        # public webservice call will just log errors
        order = self.env['sale.order'].ws_create_new(data)
        self.assertEqual(order, None)
