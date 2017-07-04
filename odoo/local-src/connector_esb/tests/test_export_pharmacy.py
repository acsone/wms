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

    @property
    def model(self):
        return self.env['res.partner']

    def setup_records(self):
        self.all_records = self.model.browse()
        self.all_records |= self.model.create({
            'name': 'Joe',
            'street': 'Chemin des Pins, 23',
            'street2': '',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': 41,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'joe@ch.ch',
        })
        # add some translation
        # for rec in self.all_records:
        #     rec.with_context(lang='nl_BE').name = rec.name + ' (NL)'

    def read_test_file(self, filename):
        path = os.path.join(
            os.path.dirname(__file__),
            'examples',
            filename
        )
        with open(path, 'r') as thefile:
            return thefile.read()

    def test_mapper(self):
        expected = {
            'Id': 1,
            'Name': 'Joe',
            'Street': 'Chemin des Pins, 23',
            'Postcode': '1010',
            'City': 'Lausanne',
            'CountryId': 41,
            'Telephone': '021123123',
            'Fax': '021121212',
            'Email': 'joe@ch.ch',
        }
        rec = self.all_records[0]
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    # def test_filename(self):
    #     today = fields.Date.today().replace('-', '')
    #     with self.backend.work_on(self.model._name) as work:
    #         writer = work.component(usage='xml.write')
    #         self.assertEqual(
    #             writer.filename(), 'Pharmacy_{}.xml'.format(today))

    # @tools.mute_logger('dicttoxml')
    # def test_record_exporter(self):
    #     records = self.all_records
    #     with self.backend.work_on(self.model._name) as work:
    #         exporter = work.component(usage='record.exporter')
    #         respath = exporter.run(records)
    #     with open(respath, 'r') as result_file:
    #         result = result_file.read()
    #     self.assertXmlEquivalentData(
    #         result, self.read_test_file('product_export_1.xml'), 'Gesart')
    #     # self.assertXmlEquivalentOutputs(
    #     #     self.flatten(result),
    #     #     self.flatten(self.read_test_file('product_export_1.xml'))
    #     # )

    # def test_record_cron_exporter(self):
    #     with self.backend.work_on(self.model._name) as work:
    #         exporter = work.component(usage='record.exporter.cron',
    #             model_name=self.model._name)

    #     items = exporter.get_items()
    #     for unwanted in self.unexportable_records:
    #         self.assertNotIn(
    #             unwanted, items,
    #             'Found: `[{default_code}] {name}`.'.format(
    #                 **unwanted.read()[0])
    #         )
