# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import md5
from datetime import datetime, timedelta
from .common import ESBXMLTestCase


class ExportBuyXGetY(ESBXMLTestCase):

    def setUp(self):
        super(ExportBuyXGetY, self).setUp()
        self.maxDiff = None
        self.setup_records()
        self.timestamp = self.env.ref(
                'connector_esb.esb_timestamp_buyx_gety')

    @property
    def model(self):
        return self.env['product.supplierinfo']

    def setup_records(self):
        self.sis = self.model.browse()
        # Promotion without start/end date
        self.si1 = self.env.ref('product.product_supplierinfo_1')
        self.si1.ratio_main_product = 6
        self.si1.ratio_promotional_product = 1
        self.sis |= self.si1
        # Promotion actual
        self.si2 = self.env.ref('product.product_supplierinfo_2')
        self.si2.ratio_main_product = 3
        self.si2.ratio_promotional_product = 1
        date_start = datetime.today() - timedelta(days=10)
        date_stop = datetime.today() + timedelta(days=10)
        self.si2.date_start = date_start
        self.si2.date_end = date_stop
        self.sis |= self.si2
        # Promotion out of date
        self.si3 = self.env.ref('product.product_supplierinfo_3')
        self.si3.ratio_main_product = 5
        self.si3.ratio_promotional_product = 2
        self.si3.date_start = '1971-02-01'
        self.si3.date_end = '1971-02-28'
        self.sis |= self.si3
        # Promotion without ratio
        self.si1 = self.env.ref('product.product_supplierinfo_4')
        self.si1.ratio_main_product = False
        self.si1.ratio_promotional_product = False
        self.sis |= self.si1

    def test_mapper(self):
        """ Testing the mapper """
        rec = self.si3
        expected = {
            'Sku': rec.product_tmpl_id.default_code,
            'AlcyonGroupId': '100',
            'QtyBuy1': 5,
            'QtyGet1': 2,
            'QtyBuy2': 0,
            'QtyGet2': 0,
            'QtyBuy3': 0,
            'QtyGet3': 0,
            'QtyBuy4': 0,
            'QtyGet4': 0,
            'QtyBuy5': 0,
            'QtyGet5': 0,
            'QtyBuy6': 0,
            'QtyGet6': 0,
            'StartDate': '19710201',
            'EndDate': '19710228',
            'CheckSum': '',
            'Action': 'Create',
        }
        # Add the checksum to expected values
        data = expected.values()
        data = [str(d) for d in data]
        data.sort()
        key = ''.join(data)
        expected['CheckSum'] = md5.new(key).hexdigest()
        self.timestamp.writer = 'local'
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(
                    mapper.map_record(rec).values(alcyon_group_id='100'),
                    expected)

    def test_get_items(self):
        """ Test that the right number of items are picked up for export """
        self.timestamp.writer = 'local'
        with self.backend.work_on(self.model._name,
                                  timestamp=self.timestamp) as work:
            exporter = work.component(usage='record.exporter.cron')
            items = self.sis.search(exporter.get_items_domain())
        self.assertEqual(len(items), 1)
