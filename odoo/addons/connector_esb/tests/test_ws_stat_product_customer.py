# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from .common import ESBXMLTestCase


class WSStatProductCustomerTestCase(ESBXMLTestCase):
    def setUp(self):
        super(WSStatProductCustomerTestCase, self).setUp()
        self.setup_records()

    def setup_records(self):
        self.customer = self.env['res.partner'].create(
            {
                'ref': '123456',
                'name': 'Joe',
                'street': 'Chemin des Pins, 23',
                'street2': '',
                'zip': '1010',
                'city': 'Lausanne',
                'country_id': 44,
                'phone': '021123123',
                'fax': '021121212',
                'email': 'joe@ch.ch',
            }
        )
        cat_materiel = self.env.ref('specific_data.product_categ_materiel')
        cat_ali = self.env.ref('specific_data.product_categ_ali')
        # Test with a sub category of medic
        cat_microb = self.env.ref('specific_data.product_categ_antimicrobiens')
        # Set up products with different category
        self.p1 = self.env.ref('product.product_product_8')
        self.p1.product_tmpl_id.categ_id = cat_microb
        self.p2 = self.env.ref('product.product_product_9')
        self.p2.product_tmpl_id.categ_id = cat_materiel
        self.p3 = self.env.ref('product.product_product_10')
        self.p3.product_tmpl_id.categ_id = cat_ali
        # One sale order for last month
        today = datetime.now()
        self.env['sale.order'].create(
            {
                'partner_id': self.customer.id,
                'date_order': today - relativedelta(months=1),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': 1,
                            'product_uom_qty': 15,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p3.name,
                            'product_id': self.p3.id,
                            'product_uom': 1,
                            'product_uom_qty': 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p2.name,
                            'product_id': self.p2.id,
                            'product_uom': 1,
                            'product_uom_qty': 15,
                        },
                    ),
                ],
            }
        )
        # One sale order for two month ago
        self.env['sale.order'].create(
            {
                'partner_id': self.customer.id,
                'date_order': today - relativedelta(months=2),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': 1,
                            'product_uom_qty': 35,
                        },
                    )
                ],
            }
        )
        # One sale order for the same month last year
        self.env['sale.order'].create(
            {
                'partner_id': self.customer.id,
                'date_order': datetime(today.year - 1, today.month, 1),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': 4,
                            'product_uom_qty': 5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p3.name,
                            'product_id': self.p3.id,
                            'product_uom': 2,
                            'product_uom_qty': 5,
                        },
                    ),
                ],
            }
        )
        # One sale order from 13 month ago to see that it is not used
        self.env['sale.order'].create(
            {
                'partner_id': self.customer.id,
                'date_order': (
                    datetime(today.year - 1, today.month, 1)
                    - relativedelta(months=1)
                ),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': 4,
                            'product_uom_qty': 13,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p3.name,
                            'product_id': self.p3.id,
                            'product_uom': 2,
                            'product_uom_qty': 33,
                        },
                    ),
                ],
            }
        )

    def test_message(self):
        backend = self.env['esb.backend'].get_singleton()
        with backend.work_on('sale.order.line') as work:
            component = work.component('ws.message.product.customer.stat')
        message = component.get_message(
            self.customer.ref, self.p1.default_code
        )
        root = self.assertXmlDocument(message)
        self.assertXpathValues(
            root, '//salesAverage/text()', ('0.00', '15.00', '5.00', '35.00')
        )
