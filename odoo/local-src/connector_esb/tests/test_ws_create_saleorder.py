# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import patch, MagicMock
from copy import deepcopy

from odoo import fields
from odoo.tests.common import SavepointCase
from odoo.addons.connector_esb.controllers.sale import SaleController
from odoo.exceptions import MissingError
from werkzeug.exceptions import BadRequest


class WSCreateSaleOrderTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(WSCreateSaleOrderTestCase, cls).setUpClass()
        cls.controller = SaleController()
        cls.fiji = cls.env.ref('base.fj')
        cls.fiji.esb_ref = 'fj'
        cls.setup_records()
        cls.order_data = {
            "increment_id": "INC-ID",
            "customer_id": cls.partner.ref,
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
        cls.order_data_cnk = {
            "increment_id": "INC-ID",
            "customer_id": cls.partner.ref,
            "date": "2017-09-18",
            "order_ref": "refClt",
            "lines": [{
                'line_id': '1',
                'cnk': '00999',
                'quantity': 3,
                'free': False,
            }]
        }
        cls.request_data = {
            "jsonrpc": "3.0", "id": "4321",
            "method": "create",
            "params": {
                "data": cls.order_data
            }
        }

    @classmethod
    def setup_records(cls):
        cls.p1 = cls.env['product.product'].create({
            'name': 'Unittest P1',
            'default_code': '0001',
            'cnk_code': '00999',
            'list_price': 10.0,
        })
        cls.delivery_1 = cls.env['delivery.carrier'].create({
            'delivery_type': 'fixed',
            'name': 'delivery carrier 1',
            'esb_ref': '031',
            })
        cls.payment_30_net = cls.env.ref('account.account_payment_term_net')
        cls.partner = cls.env['res.partner'].create(
            {'name': 'John Doe',
             'ref': '111111',
             'property_delivery_carrier_id': cls.delivery_1.id,
             'supplier_promotion_sale_allowed': True,
             'property_payment_term_id': cls.payment_30_net.id,
             }
        )
        cls.partner_shipping = cls.env['res.partner'].create({
            'name': 'John Doe (ship)',
            'ref': '58020388759284',
            'type': 'delivery',
            'street': 'Middle street 2',
            'city': 'Some Island',
            'zip': '7492125',
            'country_id': cls.fiji.id,
            'parent_id': cls.partner.id,
        })

    def test_create_saleorder(self):
        starting_date = fields.Datetime().now()
        data = deepcopy(self.order_data)
        data['num_suite'] = 'iamsuitename'
        order = self.env['sale.order']._ws_create_new(data)
        tax_rate = self.p1.taxes_id.amount / 100.0
        web_team = self.env.ref('sales_team.salesteam_website_sales')
        expected = {
            'esb_ref': 'INC-ID',
            'client_order_ref': 'refClt',
            'partner_id': self.partner,
            'partner_invoice_id': self.partner,
            'partner_shipping_id': self.partner_shipping,
            'amount_total': self.p1.list_price * 3 * (1 + tax_rate),
            'amount_tax': self.p1.list_price * 3 * tax_rate,
            'supplier_promotion_allowed': True,
            'payment_term_id': self.payment_30_net,
            'team_id': web_team,
            'sale_channel': 'web',
            'suite_name': 'iamsuitename',
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

    def test_create_saleorder_multiple_ref(self):
        self.partner_shipping.ref = self.partner.ref
        self.test_create_saleorder()

    def test_create_saleorder_shipping(self):
        carrier = self.env['delivery.carrier'].search([], limit=1)
        carrier.esb_ref = '95'
        data = deepcopy(self.order_data)
        data['carrier_id'] = carrier.esb_ref
        order = self.env['sale.order']._ws_create_new(data)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.carrier_id, carrier)

    def test_create_saleorder_shipping_use_default_from_partner(self):
        """Check the use of default delivery carrier from partner.

        When not specified in the data
        """
        data = deepcopy(self.order_data)
        order = self.env['sale.order']._ws_create_new(data)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.carrier_id, self.delivery_1)

    def test_request_data(self):
        """ Check for well formed data and some compulsory fields """
        data = deepcopy(self.request_data)
        data.pop('params')
        with self.assertRaises(BadRequest):
            self.controller._validate_request(data)

    def test_required_fields_1(self):
        data = deepcopy(self.request_data)
        data['params']['data'].pop('increment_id')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_2(self):
        data = deepcopy(self.request_data)
        data['params']['data'].pop('customer_id')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_3(self):
        data = deepcopy(self.request_data)
        data['params']['data'].pop('date')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_4(self):
        data = deepcopy(self.request_data)
        data['params']['data'].pop('lines')
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_required_fields_5(self):
        """Check lines is a list"""
        data = deepcopy(self.request_data)
        data['params']['data']['lines'] = data['params']['data']['lines'][0]
        with self.assertRaises(BadRequest):
            self.controller._validate_create_sale_order(data)

    def test_integrity_error(self):
        data = deepcopy(self.order_data)
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

    def test_create_saleorder_with_discount(self):
        discount_percent = 10.
        supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'ref': '9001',
        })
        self.p1.seller_ids = self.env['product.supplierinfo'].create({
            'name': supplier.id,
            'discount_sale': discount_percent,
        })

        starting_date = fields.Datetime().now()
        data = deepcopy(self.order_data)
        order = self.env['sale.order']._ws_create_new(data)
        tax_rate = self.p1.taxes_id.amount / 100.0
        unit_price = (self.p1.list_price -
                      self.p1.list_price * discount_percent / 100)
        expected = {
            'esb_ref': 'INC-ID',
            'client_order_ref': 'refClt',
            'partner_id': self.partner,
            'partner_invoice_id': self.partner,
            'partner_shipping_id': self.partner_shipping,
            'amount_total': unit_price * 3 * (1 + tax_rate),
            'amount_tax': unit_price * 3 * tax_rate,
            'supplier_promotion_allowed': True,
            'payment_term_id': self.payment_30_net,
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
        # check discounts
        self.assertEqual(order.order_line.discount2, discount_percent)

    def test_create_saleorder_with_cnk(self):
        data = deepcopy(self.order_data_cnk)
        order = self.env['sale.order']._ws_create_new(data)
        tax_rate = self.p1.taxes_id.amount / 100.0
        web_team = self.env.ref('sales_team.salesteam_website_sales')
        expected = {
            'esb_ref': 'INC-ID',
            'client_order_ref': 'refClt',
            'partner_id': self.partner,
            'partner_invoice_id': self.partner,
            'partner_shipping_id': self.partner_shipping,
            'amount_total': self.p1.list_price * 3 * (1 + tax_rate),
            'amount_tax': self.p1.list_price * 3 * tax_rate,
            'supplier_promotion_allowed': True,
            'payment_term_id': self.payment_30_net,
            'team_id': web_team,
            'sale_channel': 'web',
        }
        for k, v in expected.iteritems():
            if isinstance(v, float):
                self.assertAlmostEqual(order[k], v)
            else:
                self.assertEqual(order[k], v)
        self.assertEqual(len(order.order_line), 1)

    def test_create_saleorder_no_notify(self):
        """Check salesmanager won't receive a "Assigned to you" notification
        on create of sale order from WS

        """
        data = deepcopy(self.order_data)
        demo = self.env.ref('base.user_demo')
        # set a user that will be copied on sale as salesmanager
        self.partner.user_id = demo
        self.env['sale.order']._patch_method(
            'message_post_with_view', MagicMock()
        )

        self.env['sale.order']._ws_create_new(data)
        self.env['sale.order'].message_post_with_view.assert_not_called()
