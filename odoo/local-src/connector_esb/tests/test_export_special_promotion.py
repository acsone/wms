# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from .common import ESBXMLTestCase


class ExportSpecialPromotionTestCase(ESBXMLTestCase):

    def setUp(self):
        super(ExportSpecialPromotionTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref(
                'connector_esb.esb_timestamp_special_promotion')

    @property
    def model(self):
        return self.env['product.pricelist.item']

    def setup_records(self):
        # Create 2 products
        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'default_code': '0001'
        })
        self.p2 = self.env['product.product'].create({
            'name': 'Unittest P2',
            'default_code': '0002'
        })
        # Create a new pricelist with percentage discount on the product 1
        self.discount_pricelist_1 = self.env['product.pricelist'].create({
            'name': 'Discount list 1',
            'item_ids': [
                (0, False, {
                    'applied_on': '0_product_variant',
                    'product_id': self.p1.id,
                    'compute_price': 'percentage',
                    'percent_price': 5,
                    'date_start': '2017-07-12',
                    'date_end': '2017-12-31'
                }),
            ],
        })
        # Create 1 clients with the the discount pricelist 1
        self.client1 = self.env['res.partner'].create({
            'email': 'joe@ch.ch',
            'name': 'Joe',
            'lang': 'nl_BE',
            'ref': 'joe',
            'customer': True,
            'discount_pricelist_id': self.discount_pricelist_1.id,
        })
        # Create another pricelist with percentage discount on the 2 products
        self.discount_pricelist_2 = self.env['product.pricelist'].create({
            'name': 'Discount list 2',
            'item_ids': [
                (0, False, {
                    'applied_on': '0_product_variant',
                    'product_id': self.p2.id,
                    'compute_price': 'percentage',
                    'percent_price': 15,
                    'date_start': '2017-07-31',
                    'date_end': '2017-08-31',
                })
            ],
        })
        # Create another clients with the the discount pricelist 2
        self.client2 = self.env['res.partner'].create({
            'email': 'tom@ch.ch',
            'name': 'Tom',
            'lang': 'nl_BE',
            'ref': 'tom',
            'customer': True,
            'discount_pricelist_id': self.discount_pricelist_2.id,
        })

    def test_mapper(self):
        """ Testing mapper without id client """
        expected = {
            'Sku': u'0001',
            'Percent': '5.00',
            'StartDate': '20170712',
            'EndDate': '20171231',
            'Action': 'Create'
        }
        self.timestamp.writer = 'local'
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            rec = self.discount_pricelist_1.item_ids[0]
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_export(self):
        """ Make a full export check with existing xml file"""
        self.timestamp.writer = 'local'
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            respath = exporter.run()
            self.addCleanup(os.remove, respath)
            with open(respath, 'r') as result_file:
                result = result_file.read()
            self.assertXmlEquivalentData(
                result,
                self.read_test_file('special_promotion_1.xml'), 'CustomerId')
