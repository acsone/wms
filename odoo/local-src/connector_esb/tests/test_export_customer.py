# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from .common import ESBXMLTestCase


class ExportCustomerTestCase(ESBXMLTestCase):

    @classmethod
    def setUpClass(cls):
        super(ExportCustomerTestCase, cls).setUpClass()
        cls.alcyon_category = cls.env['partner.alcyon_category'].create({
            'name': 'Test partner alcyon category',
            'esb_ref': 'TST'
        })

    def setUp(self):
        super(ExportCustomerTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref('connector_esb.esb_timestamp_customer')

    @property
    def model(self):
        return self.env['res.partner']

    def setup_records(self):
        self.discount_pricelist = self.env['product.pricelist'].create({
            'name': 'Special price',
            'esb_ref': 'REF_ESB'
        })
        self.discount_pricelist_2 = self.env['product.pricelist'].create({
            'name': 'Special price 2',
            'esb_ref': 'REF_ESB_2'
        })
        self.partner_category = self.env['res.partner.category'].create({
            'name': 'Petits animaux'
        })
        # Make all existing customer not interfere with the test
        existing_customers = self.env['res.partner'].search(
                [('customer', '=', True)])
        existing_customers.write({'customer': False})
        # Create new customer to test
        self.all_records = self.model.browse()
        self.customer1 = self.model.create({
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
            'alcyon_category_id': self.alcyon_category.id,
            'discount_pricelist_id': self.discount_pricelist_2.id,
            'property_product_pricelist': self.env.ref(
                'specific_data.product_pricelist_pb1'),
            'category_id': [(4, self.partner_category.id, 0)]
        })
        self.all_records |= self.customer1
        self.all_records |= self.model.create({
            'ref': '100',
            'name': 'Peter',
            'lang': 'en_US',
            'street': 'Chemin des Oies, 1',
            'street2': u'A côté de la fontaine',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': 44,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'peter@ch.ch',
            'pharmacist_id': self.env.ref('base.main_partner').id,
            'customer': True,
            'alcyon_category_id': self.alcyon_category.id,
            'discount_pricelist_id': self.discount_pricelist.id,
        })
        # This one should not be processed because not a customer type
        self.all_records |= self.model.create({
            'ref': '101',
            'name': 'Peter',
            'lang': 'en_US',
            'street': 'Chemin des Oies, 1',
            'street2': u'A côté de la fontaine',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': 44,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'peter@ch.ch',
            'pharmacist_id': self.env.ref('base.main_partner').id,
            'alcyon_category_id': self.alcyon_category.id,
            'customer': False,
        })
        # This one should not be processed because it has a parent
        self.all_records |= self.model.create({
            'ref': '102',
            'name': 'Peter',
            'lang': 'en_US',
            'street': 'Chemin des Oies, 1',
            'street2': u'A côté de la fontaine',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': 44,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'peter@ch.ch',
            'pharmacist_id': self.env.ref('base.main_partner').id,
            'customer': True,
            'parent_id': self.all_records[0].id
        })
        # A sale order to test SerialNo
        self.so = self.env['sale.order'].create({
            'partner_id': self.customer1.id,
            'suite_name': '321123'
        })

    def test_mapper(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'Email': u'joe@ch.ch',
            'Firstname': u'Joe',
            'Language': u'TLH',
            'GroupId': self.alcyon_category.esb_ref,
            'Taxvat': u'BE0477472701',
            'IdRound': '0000',
            'IdDelegate': '',
            'IdPharmacy': '',
            'TaxCode': 0,
            'OnlinePayment': False,
            'DepositNumber': u'2/1234/1234',
            'ErpId': u'3162',
            'AlcyonGroupId': self.discount_pricelist_2.esb_ref,
            u'Petits_animaux': 'Y',
            'StatisticCode': '10',
            'SerialNo': '321123',
            'ShowTimer': True,
            }
        self.timestamp.writer = 'local'
        rec = self.customer1
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_IdRound_mapper(self):
        """ Testing the mapper of IdRound

        Easier to fake the model than trying to set up the data in the db with
        values.
        """
        class FakeModel(object):
            def __init__(self, tlo):
                self.time_limit_order = tlo

        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            result = mapper.compute_idround(FakeModel(1.25))
            self.assertEqual(result['IdRound'], '0115')
            result = mapper.compute_idround(FakeModel(0.50))
            self.assertEqual(result['IdRound'], '0030')
            result = mapper.compute_idround(FakeModel(4.75))
            self.assertEqual(result['IdRound'], '0445')
            result = mapper.compute_idround(FakeModel(2))
            self.assertEqual(result['IdRound'], '0200')
            result = mapper.compute_idround(FakeModel(0))
            self.assertEqual(result['IdRound'], '0000')

    def test_filename(self):
        self.check_filename('Customer_{0}_{1}.xml')

    def test_only_customer_exported(self):
        """ Not all res_partner should be exported """
        self.timestamp.writer = 'local'
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            items = exporter.get_items(self.timestamp.last_export)
            self.assertEqual(len(items & self.all_records), 2)

    def test_export(self):
        """ """
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
                self.read_test_file('customer_1.xml'),
                'Firstname')
