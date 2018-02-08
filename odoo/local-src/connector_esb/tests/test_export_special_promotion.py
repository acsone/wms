# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import md5
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
        return self.env['product.supplierinfo']

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
        # Create a supplier
        self.supplier1 = self.env['res.partner'].create({
            'ref': 'J',
            'name': 'Joe',
            'street': 'Chemin des Pins, 23',
            'street2': '',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': 44,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'joe@ch.ch',
            'supplier': True,
        })
        self.psi1 = self.model.create({
            'delay': 3,
            'currency_id': self.env.user.company_id.currency_id.id,
            'name': self.supplier1.id,
            'product_id': self.p1.id,
            'discount_sale': 5,
            'date_start': '2017-07-12',
            'date_end': '2017-12-31',
            'min_qty': 5,
            'price': 123,
            })
        self.psi2 = self.model.create({
            'delay': 4,
            'currency_id': self.env.user.company_id.currency_id.id,
            'name': self.supplier1.id,
            'product_id': self.p2.id,
            'discount_sale': 15,
            'date_start': '2017-07-31',
            'date_end': '2017-08-31',
            'min_qty': 4,
            'price': 321,
            })

    def test_mapper(self):
        """ Testing mapper without id client """
        expected = {
            'Sku': u'0001',
            'Percent1': '5.00',
            'Percent2': '0',
            'StartDate': '20170712',
            'EndDate': '20171231',
            'AlcyonGroupId': '',
            'Action': 'Create',
        }
        # Add the checksum to expected values
        data = expected.values()
        data.sort()
        key = ''.join(data)
        expected['CheckSum'] = md5.new(key).hexdigest()
        self.timestamp.writer = 'local'
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            rec = self.psi1
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
                self.read_test_file('special_promotion_1.xml'), 'Sku')
