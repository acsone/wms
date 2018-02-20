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
        # Create a customer with a delivery address
        self.partner_2 = self.model.create({
            'name': 'Company 2',
            'street': 'Main Street, 2',
            'ref': None,
            'zip': '123123',
            'city': 'Paradise',
            'country_id': 44,
        })
        self.partner_2_delivery = self.model.create({
            'ref': 'ref-delivery',
            'name': 'delivery-address',
            'street': 'street 1',
            'street2': '',
            'zip': 'zip',
            'city': 'TheCity',
            'country_id': 44,
            'parent_id': self.partner_2.id,
            'type': 'delivery'
        })

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

    def test_mapper_for_shipping_address_without(self):
        """ Generate dict with the mapper and compare with what is expected

        No specific shipping address so use the client default
        """
        expected = {
            'CustomerId': self.main_partner.ref,
            # If shipping address does not exist !
            'AddressId': '0',
            'City': self.main_partner.city,
            'CountryId': self.country44.esb_ref,
            'Firstname': self.main_partner.name,
            'Postcode': self.main_partner.zip,
            'Street': self.main_partner.street,
            'IsDefaultBilling': False,
            'IsDefaultShipping': True,
        }
        rec = self.main_partner
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(
                mapper.map_record(rec).values(address_kind='delivery'),
                expected)

    def test_mapper_for_shipping_address_with(self):
        """ Generate dict with the mapper and compare with what is expected

        A specific shipping address is set for the client
        """
        expected = {
            # Testing empty ref should not be false but empty string
            'CustomerId': '',
            # Shipping address exists !
            'AddressId': 'ref-delivery',
            'City': self.partner_2_delivery.city,
            'CountryId': self.country44.esb_ref,
            'Firstname': self.partner_2_delivery.name,
            'Postcode': self.partner_2_delivery.zip,
            'Street': self.partner_2_delivery.street,
            'IsDefaultBilling': False,
            'IsDefaultShipping': True,
        }
        rec = self.partner_2_delivery
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(
                mapper.map_record(rec).values(address_kind='delivery'),
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
