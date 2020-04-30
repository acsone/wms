# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
import zipfile

from .common import ESBXMLTestCase


class ExportDocumentZipTestCase(ESBXMLTestCase):
    def setUp(self):
        super(ExportDocumentZipTestCase, self).setUp()
        self.setup_records()
        self.timestamp = self.env.ref(
            'connector_esb.esb_timestamp_document_zip'
        )

    @property
    def model(self):
        return self.env['ir.attachment']

    def setup_records(self):
        self.all_records = self.model.browse()
        self.filedata_1 = 'this is a test file'
        self.filename_1 = 'NE_alsfja.csv'
        self.filename_2 = 'CM_alkdsjf.pdf'
        # Creating a good looking attachment
        self.all_records |= self.model.create(
            {
                'type': 'binary',
                'res_model': 'stock.picking',
                'name': self.filename_1,
                'datas_fname': self.filename_1,
                'mimetype': 'text/plain',
                'datas': self.filedata_1.encode('base_64'),
            }
        )
        # Creating an attachment with no data
        self.all_records |= self.model.create(
            {
                'type': 'binary',
                'res_model': 'stock.picking',
                'name': self.filename_2,
                'datas_fname': self.filename_2,
                'mimetype': 'text/pdf',
                # no 'datas' to check it does not fail
            }
        )

    def test_mapper(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            'filename': self.filename_1,
            'data': self.filedata_1.encode('base_64'),
        }
        rec = self.all_records[0]
        with self.backend.work_on(self.model._name) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_record_exporter_local(self):
        """ Use the exporter to create the zip file and check our file"""
        self.timestamp.writer = 'local'
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage='record.exporter.cron')
            respath = exporter.run()
            self.addCleanup(os.remove, respath)
        self.assertTrue(zipfile.is_zipfile(respath))
        with zipfile.ZipFile(respath, 'r') as zf:
            namelist = zf.namelist()
            self.assertTrue(self.filename_1 in namelist)
