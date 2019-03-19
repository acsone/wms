# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields

from .common import ESBXMLTestCase


class WSCustomerDeliveryFeeTestCase(ESBXMLTestCase):
    def setUp(self):
        super(WSCustomerDeliveryFeeTestCase, self).setUp()
        self.setup_records()

    @property
    def model(self):
        return self.env['res.partner']

    def setup_records(self):
        self.customer_1 = self.model.create(
            {
                'email': 'joe@ch.ch',
                'name': 'Joe',
                'lang': 'tlh_TLH',
                'vat': 'BE0477472701',
                'user_id': '',
                'vet_depot_number': '2/1234/1234',
                'ref': '3162',
                'street': 'Chemin des Pins, 23',
                'street2': '',
                'zip': '1010',
                'city': 'Lausanne',
                'country_id': 44,
                'phone': '021123123',
                'fax': '021121212',
                'customer': True,
            }
        )
        self.customer_2 = self.model.create(
            {
                'email': 'deux@ch.ch',
                'name': 'Deux',
                'lang': 'tlh_TLH',
                'vat': 'BE0477472701',
                'user_id': '',
                'vet_depot_number': '2/1234/1234',
                'ref': '0002',
                'street': 'Chemin des Pins, 23',
                'street2': '',
                'zip': '1010',
                'city': 'Lausanne',
                'country_id': 44,
                'phone': '021123123',
                'fax': '021121212',
                'customer': True,
            }
        )
        # Set up products with different category
        self.p1 = self.env.ref('product.product_product_8')
        self.p2 = self.env.ref('product.product_product_9')
        self.p3 = self.env.ref('product.product_product_10')
        # Set up sale orders for customer 1
        self.so1 = self.env['sale.order'].create(
            {
                'partner_id': self.customer_1.id,
                'date_order': fields.Datetime.now(),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom_qty': 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p3.name,
                            'product_id': self.p3.id,
                            'product_uom_qty': 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p2.name,
                            'product_id': self.p2.id,
                            'product_uom_qty': 15,
                        },
                    ),
                ],
            }
        )
        self.so1.action_confirm()
        self.so2 = self.env['sale.order'].create(
            {
                'partner_id': self.customer_1.id,
                'date_order': datetime.now() - timedelta(days=400),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom_qty': 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p3.name,
                            'product_id': self.p3.id,
                            'product_uom_qty': 5,
                        },
                    ),
                ],
            }
        )

    def test_fix_value(self):
        """This web service returns always the same value"""
        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('res.partner') as work:
            component = work.component('ws.message.customer.delivery.fee')
            message = component.get_message(self.customer_1.ref)
        self.assertXmlEquivalentData(
            message,
            self.read_test_file('delivery_fee_ws_1.xml'),
            'totalOrderAmount',
        )
