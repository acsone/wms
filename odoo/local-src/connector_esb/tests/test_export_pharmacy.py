# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools, fields
from .common import ESBXMLTestCase


class ExportPharmacyTestCase(ESBXMLTestCase):

    def setUp(self):
        super(ExportPharmacyTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref('connector_esb.esb_timestamp_pharmacy')

    @property
    def model(self):
        return self.env['res.partner']

    def setup_records(self):
        self.country_ch = self.env['res.country'].search(
                [('code', '=', 'CH')])[0]
        self.all_records = self.model.browse()
        self.all_records |= self.model.create({
            'ref': 'J',
            'name': 'Joe',
            'street': 'Chemin des Pins, 23',
            'street2': '',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': self.country_ch.id,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'joe@ch.ch',
        })
        self.pharmacist_1 = self.model.create({
            'ref': 'P',
            'name': 'Peter',
            'street': 'Chemin des Oies, 1',
            'street2': u'A côté de la fontaine',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': self.country_ch.id,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'peter@ch.ch',
        })
        self.all_records |= self.pharmacist_1
        self.all_records |= self.model.create({
            'ref': 'O',
            'name': 'Olson',
            'street': 'Chemin des Canards, 1',
            'zip': '1003',
            'city': 'Geneve',
            'country_id': self.country_ch.id,
            'phone': '021123123',
            'fax': '021121212',
        })
        self.client_1 = self.env.ref('base.main_partner')
        self.client_2 = self.model.create({
            'ref': 'client_1',
            'name': 'Yoyo',
            'country_id': self.country_ch.id,
        })
        # Affect to the clients the pharmacist
        self.client_1.pharmacist_id = self.pharmacist_1
        self.client_2.pharmacist_id = self.pharmacist_1
        self.country_ch.esb_ref = 'HOP'

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
            'CountryId': self.country_ch.esb_ref,
            }
        rec = self.all_records[0]
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_mapper_street_multi_line(self):
        """ Test the mapper with multi line for street """
        expected = {
            'Id': 'P',
            'Name': 'Peter',
            'Postcode': '1010',
            'City': 'Lausanne',
            'Telephone': '021123123',
            'Fax': '021121212',
            'Email': 'peter@ch.ch',
            'Street': u'Chemin des Oies, 1\nA côté de la fontaine',
            'CountryId': self.country_ch.esb_ref,
            }
        rec = self.all_records[1]
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_mapper_empty_email(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'Id': 'O',
            'Name': 'Olson',
            'Postcode': '1003',
            'City': 'Geneve',
            'Telephone': '021123123',
            'Fax': '021121212',
            'Street': 'Chemin des Canards, 1',
            'CountryId': self.country_ch.esb_ref,
            }
        rec = self.all_records[2]
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_filename(self):
        self.check_filename('Pharmacy_{}.xml')

    @tools.mute_logger('dicttoxml')
    def test_record_exporter_local(self):
        """ Export, create xml file and compare with the one in example """
        self.timestamp.writer = 'local'
        records = self.all_records
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter')
            respath = exporter.run(records)
        with open(respath, 'r') as result_file:
            result = result_file.read()
        self.assertXmlEquivalentData(
            result, self.read_test_file('pharmacy_export_1.xml'), 'Id')

    def test_no_update_since_last_export(self):
        """ Test timestamp should return no records"""
        record = self.model.create({
            'ref': 'R',
            'name': 'Roland',
            'street': 'Chemin des Canards, 1',
            'street2': u'De l\'autre côté de la fontaine',
            'zip': '1010',
            'city': 'Lausanne',
            'country_id': self.country_ch.id,
            'phone': '021123123',
            'fax': '021121212',
            'email': 'roland@ch.ch',
        })
        self.env.ref('base.partner_root').pharmacist_id = record
        self.all_records |= record
        self.timestamp.last_export = False
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(
                usage='record.exporter.cron',
                model_name=self.model._name
            )
            items = exporter.get_items(export_since=self.timestamp.last_export)
            # export 2 partners
            self.assertEqual(len(items), 2)

        self.timestamp.last_export = fields.Datetime.now()
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(
                usage='record.exporter.cron',
                model_name=self.model._name
            )
            items = exporter.get_items(export_since=self.timestamp.last_export)
            # no partner modified since last export
            self.assertEqual(len(items), 0)

        # an ORM write in a test does not change the write_date...
        self.env.cr.execute("""
            UPDATE res_partner SET write_date = %s WHERE id = %s
        """, (fields.Datetime.now(), record.id))
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(
                usage='record.exporter.cron',
                model_name=self.model._name
            )
            items = exporter.get_items(export_since=self.timestamp.last_export)
            # 1 partner modified since last export
            self.assertEqual(len(items), 1)

    def test_record_cron_exporter(self):
        """Test that our pharmacist who has two clients get exported"""
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(
                usage='record.exporter.cron',
                model_name=self.model._name
            )

        items = exporter.get_items('')
        self.assertEqual(len(items), 1)

    def test_record_cron_exporter_2(self):
        """Pharmacist with one client active and one not, should be exported"""
        # So lets set one client of our pharmacist to inactive
        self.client_1.active = False
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(
                usage='record.exporter.cron',
                model_name=self.model._name
            )
        items = exporter.get_items('')
        self.assertEqual(len(items), 1)

    def test_record_cron_exporter_3(self):
        """Pharmacist whose all clients are inactive should not be exported"""
        # So lets set the client of our pharmacist to inactive
        self.client_1.active = False
        self.client_2.active = False
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(
                usage='record.exporter.cron',
                model_name=self.model._name
            )
        items = exporter.get_items('')
        self.assertEqual(len(items), 0)
