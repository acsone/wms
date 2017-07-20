# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from odoo import fields
from .common import ESBXMLTestCase


class ExportCustomerAddressTestCase(ESBXMLTestCase):

    def setUp(self):
        super(ExportCustomerAddressTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref(
                'connector_esb.esb_timestamp_customer_address')

    @property
    def model(self):
        return self.env['res.partner']

    def setup_records(self):
        self.country44 = self.env['res.country'].search([('id', '=', 44)])
        self.country44.esb_ref = 'ESB'
        self.all_records = self.model.browse()
        # Create a customer with two addresses
        self.main_partner = self.model.create({
            'name': 'Company 1',
            'ref': 'refno'
        })
        self.all_records |= self.main_partner
        # With both type of addresses invoice and delivery
        self.all_records |= self.model.create({
            'ref': 'ref-invoice',
            'street': 'Some streets in one line',
            'street2': '',
            'zip': 'xyz',
            'city': 'Kloten',
            'country_id': 44,
            'phone': '021123123',
            'fax': '',
            'parent_id': self.main_partner.id,
            'type': 'invoice'
        })
        self.all_records |= self.model.create({
            'ref': 'ref-delivery',
            'street': 'Some streets in two line',
            'street2': 'Second line, here',
            'city': 'Bern',
            'country_id': 44,
            'phone': '',
            'fax': '0123123123',
            'parent_id': self.main_partner.id,
            'type': 'delivery'
        })
        # Create an other customer with only one address
        self.main_partner2 = self.model.create({
            'name': 'Company 2',
            'ref': 'refno2'
        })
        self.all_records |= self.main_partner2
        # With both type of addresses invoice and delivery
        self.all_records |= self.model.create({
            'ref': 'ref-delivery',
            'name': 'contact-name',
            'street': 'Some streets in two line',
            'street2': '2nd line',
            'zip': 'xyz',
            'city': 'Genf',
            'country_id': 44,
            'phone': '',
            'fax': '',
            'parent_id': self.main_partner2.id,
            'type': 'delivery'
        })

    def test_filename(self):
        today = fields.Date.today().replace('-', '')
        time = fields.Datetime.now().split(' ')[1].replace(':', '')
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            expected = 'CustomerAddress_{0}_{1}.xml'.format(today, time)
            writer = work.component(usage='local.xml.writer')
            self.assertEqual(
                writer.filename(), expected)
            writer = work.component(usage='sftp.xml.writer')
            self.assertEqual(
                writer.filename(), expected)

    def test_mapper_customer_with_two_address(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'CustomerId': self.main_partner.ref,
            'AddressId': u'ref-invoice',
            'City': u'Kloten',
            'CountryId': self.country44.esb_ref,
            'Firstname': '',
            'Postcode': u'xyz',
            'Telephone': u'021123123',
            'Street': u'Some streets in one line',
            'IsDefaultBilling': True,
            'IsDefaultShipping': False,
        }
        rec = self.all_records[1]
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_mapper_customer_with_one_address(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'CustomerId': self.main_partner2.ref,
            'AddressId': u'ref-delivery',
            'City': u'Genf',
            'CountryId': self.country44.esb_ref,
            'Firstname': u'contact-name',
            'Postcode': u'xyz',
            'Street': u'Some streets in two line\n2nd line',
            'IsDefaultBilling': True,
            'IsDefaultShipping': True,
        }
        rec = self.all_records[4]
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_export(self):
        """ Run export and compare with example file"""
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
                self.read_test_file('customer_address_1.xml'),
                'City')
