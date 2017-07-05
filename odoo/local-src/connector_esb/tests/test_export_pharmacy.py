# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools, fields
from .common import ESBXMLTestCase
import os


class ExportPharmacyTestCase(ESBXMLTestCase):

    def setUp(self):
        super(ExportPharmacyTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None

    @property
    def model(self):
        return self.env['res.partner']

    def setup_records(self):
        self.all_records = self.model.browse()
        self.all_records |= self.model.create({
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
        })
        self.all_records |= self.model.create({
            'ref': 'P',
            'name': 'Peter',
            'street': 'Chemin des Oies, 1',
            'street2': 'A côté de la fontaine',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': 44,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'peter@ch.ch',
            'pharmacist_id': 1
        })

    def read_test_file(self, filename):
        path = os.path.join(
            os.path.dirname(__file__),
            'examples',
            filename
        )
        with open(path, 'r') as thefile:
            return thefile.read()

    def test_mapper(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'Id': 'J',
            'Name': 'Joe',
            'Postcode': '1010',
            'City': 'Lausanne',
            'Telephone': '021123123',
            'Fax': '021121212',
            'Email': 'joe@ch.ch',
            'Street': 'Chemin des Pins, 23',
            'CountryId': 'CH',
            }
        rec = self.all_records[0]
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    # def test_mapper_street_multi_line(self):
    #     """ Test the mapper with multi line for street """
    #     expected = {
    #         'Id': 'P',
    #         'Name': 'Peter',
    #         'Postcode': '1010',
    #         'City': 'Lausanne',
    #         'Telephone': '021123123',
    #         'Fax': '021121212',
    #         'Email': 'peter@ch.ch',
    #         'Street': 'Chemin des Oies, 1\rA côté de la fontaine',
    #         'CountryId': 'CH',
    #         }
    #     rec = self.all_records[1]
    #     with self.backend.work_on(self.model._name) as work:
    #         mapper = work.component(usage='export.mapper')
    #         self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_filename(self):
        today = fields.Date.today().replace('-', '')
        with self.backend.work_on(self.model._name) as work:
            writer = work.component(usage='xml.write')
            self.assertEqual(
                writer.filename(), 'Pharmacy_{}.xml'.format(today))

    @tools.mute_logger('dicttoxml')
    def test_record_exporter(self):
        """ Export, create xml file and compare with the one in example """
        records = self.all_records
        with self.backend.work_on(self.model._name) as work:
            exporter = work.component(usage='record.exporter')
            respath = exporter.run(records)
        with open(respath, 'r') as result_file:
            result = result_file.read()
        self.assertXmlEquivalentData(
            result, self.read_test_file('pharmacy_export_1.xml'),'Gesart')
        # self.assertXmlEquivalentOutputs(
        #     self.flatten(result),
        #     self.flatten(self.read_test_file('product_export_1.xml'))
        # )

    def test_no_update_since_last_export(self):
        """ Test timestamp should return no records"""

        le = self.env['esb.backend.timestamp'].get_last_export_time(
            self.model._name, self.backend.id, '')
        print "------>"
        print le
        # Set timestamp to now
        self.env['esb.backend.timestamp'].create({
            'backend_id': self.backend.id,
            'model': self.model._name,
            'last_export': (fields.Datetime.now()),
            'kind': ''
        })
        le = self.env['esb.backend.timestamp'].get_last_export_time(
            self.model._name, self.backend.id, '')
        print "------>"
        print le
        print "<-----"
        with self.backend.work_on(self.model._name) as work:
            exporter = work.component(usage='record.exporter.cron',
                model_name=self.model._name)
        items = exporter.get_items()
        self.assertEqual(len(items), 0)

    def test_record_cron_exporter(self):
        with self.backend.work_on(self.model._name) as work:
            exporter = work.component(usage='record.exporter.cron',
                model_name=self.model._name)

        items = exporter.get_items()
        print items
        self.assertEqual(len(items), 1)
        #exporter.run()

    #    for unwanted in self.unexportable_records:
    #         self.assertNotIn(
    #             unwanted, items,
    #             'Found: `[{default_code}] {name}`.'.format(
    #                 **unwanted.read()[0])
    #         )
