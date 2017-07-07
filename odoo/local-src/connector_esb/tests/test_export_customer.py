# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from .common import ESBXMLTestCase


class ExportCustomerTestCase(ESBXMLTestCase):

    def setUp(self):
        super(ExportCustomerTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref('connector_esb.esb_timestamp_customer')

    @property
    def model(self):
        return self.env['res.partner']

    def setup_records(self):
        self.alcyon_category = self.env['partner.alcyon_category'].create({
            'name': 'Test partner alcyon category',
            'esb_ref': 'TST'
        })
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
        self.all_records |= self.model.create({
            'email': 'joe@ch.ch',
            'name': 'Joe',
            'lang': 'nl_BE',
            'vat': 'BE0477472701',
            'user_id': '',
            'depot_number': '2/1234/1234',
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
            'property_product_pricelist': self.discount_pricelist.id,
            'category_id': [(4, self.partner_category.id, 0)]
        })
        self.all_records |= self.model.create({
            'ref': 'P',
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
            'ref': 'P',
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
            'ref': 'P',
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

    def test_mapper(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'Email': u'joe@ch.ch',
            'Username': '',
            'Firstname': u'Joe',
            'Language': u'NL',
            'GroupId': self.alcyon_category.esb_ref,
            'Taxvat': u'BE0477472701',
            'IdRound': '',
            'IdDelegate': '',
            'IdPharmacy': '',
            'TaxCode': 1,
            # OnlinePayment
            # FreeShipping,
            'DepositNumber': u'2/1234/1234',
            # ContactName
            'ErpId': u'3162',
            'AlcyonGroupId': self.discount_pricelist_2.esb_ref,
            'BackordersEnable': 1,
            'Lapsing': False,
            'LapsingDuration': 0,
            u'Petits_animaux': 'Y',
            'StatisticCode': self.discount_pricelist.esb_ref,
            'IsActive': '',
            'Password': '',
            'SerialNo': '',
            'StoreId': '',
            'ShowTimer': True,
            'WebsiteId': '',
            'MsrpSticker': False,

            }
        self.timestamp.writer = 'local'
        rec = self.all_records[0]
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_filename(self):
        today = fields.Date.today().replace('-', '')
        time = fields.Datetime.now().split(' ')[1].replace(':', '')
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            expected = 'Customer_{0}_{1}.xml'.format(today, time)
            writer = work.component(usage='local.xml.writer')
            self.assertEqual(
                writer.filename(), expected)
            writer = work.component(usage='sftp.xml.writer')
            self.assertEqual(
                writer.filename(), expected)

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
        self.delete_test_file()
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            respath = exporter.run()
            with open(respath, 'r') as result_file:
                result = result_file.read()
            self.assertXmlEquivalentData(
                result,
                self.read_test_file('customer_1.xml'),
                'Firstname')
