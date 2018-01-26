# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
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
        # Create a customer with an invoicing address but no delivery address
        self.main_partner = self.model.create({
            'name': 'Company 1',
            'street': 'Main Street, 2',
            'ref': 'refclient',
            'zip': '999888',
            'city': 'Armagedon',
            'country_id': 44,
        })
        self.all_records |= self.main_partner
        self.main_partner_invoice = self.model.create({
            'ref': 'ref-invoice',
            'name': 'invoicing-address',
            'street': 'Some streets in one line',
            'street2': '',
            'zip': 'xyz',
            'city': 'Somewhere very far away',
            'country_id': 44,
            'phone': '021123123',
            'fax': '',
            'parent_id': self.main_partner.id,
            'type': 'invoice'
        })
        self.all_records |= self.main_partner_invoice

    def test_filename(self):
        self.check_filename('CustomerAddress_{0}_{1}.xml')

    def test_mapper_for_billing_address(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'CustomerId': self.main_partner.ref,
            'AddressId': self.main_partner_invoice.ref,
            'City': self.main_partner_invoice.city,
            'CountryId': self.country44.esb_ref,
            'Firstname': self.main_partner_invoice.name,
            'Postcode': self.main_partner_invoice.zip,
            'Telephone': self.main_partner_invoice.phone,
            'Street': u'Some streets in one line',
            'IsDefaultBilling': True,
            'IsDefaultShipping': False,
        }
        rec = self.main_partner_invoice
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(
                mapper.map_record(rec).values(address_kind='invoice'),
                expected)

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
