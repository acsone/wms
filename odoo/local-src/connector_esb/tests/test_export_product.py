# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools, fields
from .common import ESBXMLTestCase


class ExportProductTestCase(ESBXMLTestCase):

    def setUp(self):
        super(ExportProductTestCase, self).setUp()
        self.setup_records()
        self.timestamp = self.env.ref('connector_esb.esb_timestamp_product')

    @property
    def model(self):
        return self.env['product.product']

    def setup_records(self):
        supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        self.all_records = self.model.browse()
        self.all_records |= self.model.create({
            'name': 'Export me pls',
            'default_code': 'exportable001',
            'barcode': 'XXX0001',
            'weight': 10.0,
            'seller_ids': [
                (0, 0, {
                    'name': supplier.id,
                    'product_code': 'supplier001',
                })],
        })
        self.all_records |= self.model.create({
            'name': 'Export me pls 2',
            'default_code': 'exportable002',
            'barcode': 'XXX0002',
            'weight': 5.0,
            'seller_ids': [
                (0, 0, {
                    'name': supplier.id,
                    'product_code': 'supplier002',
                })],
        })
        self.all_records |= self.model.create({
            'name': 'Export me pls 3',
            'default_code': 'exportable003',
            'barcode': 'XXX0003',
            'weight': 2.5,
            'seller_ids': [
                (0, 0, {
                    'name': supplier.id,
                    'product_code': 'supplier003',
                })],
        })
        # add some translation
        for rec in self.all_records:
            rec.with_context(lang='nl_BE').name = rec.name + ' (NL)'

        self.unexportable_records = self.model.browse()
        nx1 = self.model.create({
            'name': 'DO NOT Export me',
            # default_code starts with `8888`
            'default_code': '8888_not_exportable001',
        })
        self.all_records |= nx1
        self.unexportable_records |= nx1
        nx2 = self.model.create({
            'name': 'DO NOT Export me 2',
            'default_code': 'not_exportable002',
        })
        # too old
        self.force_create_date(nx2.id, '2014-7-28 00:00:00')
        self.all_records |= nx2
        self.unexportable_records |= nx2

        # TODO: add 3rd condition based on "GESCHR!=’L’ (non livrables)"
        # self.all_records |= self.model.create({
        #     'name': 'DO NOT Export me 3',
        #     'default_code': '8888_not_exportable003',
        # })

    def force_create_date(self, item_id, dt):
        self.env.cr.execute(
            'UPDATE {} SET create_date=%s '
            'WHERE id=%s'.format(self.model._table),
            (dt, item_id)
        )

    def test_mapper(self):
        expected = {
            'Gesdem': 'Export me pls',
            'Gesart': 'exportable001',
            'Cplz05': 'XXX0001',
            'Gespnt': 10.0,
            'Refdem': 'Export me pls (NL)',
            'Gesarc': 'supplier001',
            # fixed values
            'Cp2z22': '',
            'Warceg': '',
            'Warcfr': '',
            'Warcnl': '',
            'Gescsg': 0,
            'Cp2z02': 0,
            'Cp2z23': 0,
            'Cp2z24': 0,
            'Cplz29': 0,
            'Cp2z17': 0,
            'Cp2z19': 0,
            # TODO
            'Gesfou': '',
            'Cplz25': '',
            'Gesunv': '',
            'Gescrt': '2017/07/04',
            'Cplz19': '1',
            'Gescde': '1',
            'Cp2z08': '1.0',
            'Gesctv': '',
            'Gescsa': '1',
            'LotEch': '2017/11/16',
            'Cplz03': '',
            'Gescge': '0',
            'Gescov': '',
            'Cplz07': '',
            'Cplz14': '',
            'Cp2z01': '2.0',
            'Cp2z03': '2.5',
            'Cp2z05': '3.0',
            'GMA': '',
            'ALI': '',
            'ALG': '',
            'ALH': '',
            'IMP': '',
        }
        rec = self.all_records[0]
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_filename(self):
        today = fields.Date.today().replace('-', '')
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            expected = 'Product_{}.xml'.format(today)
            writer = work.component(usage='local.xml.writer')
            self.assertEqual(
                writer.filename(), expected)
            writer = work.component(usage='sftp.xml.writer')
            self.assertEqual(
                writer.filename(), expected)

    @tools.mute_logger('dicttoxml')
    def test_record_exporter_local(self):
        self.timestamp.writer = 'local'
        records = self.all_records - self.unexportable_records
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter')
            respath = exporter.run(records)
        with open(respath, 'r') as result_file:
            result = result_file.read()
        self.assertXmlEquivalentData(
            result, self.read_test_file('product_export_1.xml'), 'Gesart')
        # self.assertXmlEquivalentOutputs(
        #     self.flatten(result),
        #     self.flatten(self.read_test_file('product_export_1.xml'))
        # )

    def test_record_cron_exporter(self):
        self.timestamp.writer = 'local'
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')

        items = exporter.get_items()
        for unwanted in self.unexportable_records:
            self.assertNotIn(
                unwanted, items,
                'Found: `[{default_code}] {name}`.'.format(
                    **unwanted.read()[0])
            )
