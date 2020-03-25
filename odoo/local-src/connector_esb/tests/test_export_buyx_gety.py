# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import fields

from .common import ESBXMLTestCase


class ExportBuyXGetY(ESBXMLTestCase):
    def setUp(self):
        super(ExportBuyXGetY, self).setUp()
        self.maxDiff = None
        self.setup_records()
        self.timestamp = self.env.ref('connector_esb.esb_timestamp_buyx_gety')

    @property
    def model(self):
        return self.env['product.supplierinfo.esbflux']

    def setup_records(self):
        self.partner = self.env.ref('base.res_partner_1')
        self.prod_1 = self.env.ref(
            'product.product_product_1_product_template'
        )
        self.prod_1.default_code = ('TST',)
        self.date_start = fields.Datetime.to_string(
            datetime.now() - timedelta(days=365)
        )
        self.date_end = fields.Datetime.to_string(
            datetime.now() + timedelta(days=365)
        )
        self.sis = self.model.browse()
        # Promotion without start/end date
        self.si1 = self.model.create(
            {
                'product_tmpl_id': self.prod_1.id,
                'ratio_main_product': 6,
                'ratio_promotional_product': 1,
                'date_start': None,
                'date_end': None,
                'flux': 'buyxgety',
                'action': 'create',
            }
        )
        self.sis |= self.si1
        # Promotion actual
        self.si2 = self.model.create(
            {
                'product_tmpl_id': self.prod_1.id,
                'ratio_main_product': 3,
                'ratio_promotional_product': 1,
                'date_start': datetime.today() - timedelta(days=10),
                'date_end': datetime.today() + timedelta(days=10),
                'flux': 'buyxgety',
                'action': 'create',
            }
        )
        self.sis |= self.si2
        # Promotion out of date
        self.si3 = self.model.create(
            {
                'product_tmpl_id': self.prod_1.id,
                'ratio_main_product': 3,
                'ratio_promotional_product': 1,
                'date_start': '1971-02-01',
                'date_end': '1971-02-28',
                'flux': 'buyxgety',
                'action': 'create',
            }
        )
        self.sis |= self.si3

    def test_mapper(self):
        """ Testing the mapper """
        rec = self.si3
        expected = {
            'Sku': rec.product_tmpl_id.default_code,
            'AlcyonGroupId': '100',
            'QtyBuy1': 3,
            'QtyGet1': 1,
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
            'CheckSum': ''.join([str(rec.real_id), '100', 'buyxgety']),
            'Action': 'Create',
        }
        self.timestamp.writer = 'local'
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(
                mapper.map_record(rec).values(alcyon_group_id='100'), expected
            )

    def test_get_items(self):
        """ Test that the right number of items are picked up for export """
        self.timestamp.writer = 'local'
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage='record.exporter.cron')
            items = self.sis.search(exporter.get_items_domain())
        self.assertEqual(len(items), 1)

    def test_checksum(self):
        """Check checksum correctness.

        The checksum for different action of a promotion have to be the same.
        The checksum for action on different promotion must be different.
        """
        promo1 = self.env['product.supplierinfo'].create(
            {
                'name': self.partner.id,
                'product_tmpl_id': self.prod_1.id,
                'ratio_main_product': 5,
                'ratio_promotional_product': 1,
                'date_start': '2019-01-30',
                'date_end': '2019-03-30',
            }
        )
        promo1.discount_sale = 3
        promo2 = self.env['product.supplierinfo'].create(
            {
                'name': self.partner.id,
                'product_tmpl_id': self.prod_1.id,
                'ratio_main_product': 5,
                'ratio_promotional_product': 1,
                'date_start': '2019-07-30',
                'date_end': '2019-09-30',
            }
        )
        promo2.discount_sale = 2
        flux_promo1 = self.model.search([('real_id', '=', promo1.id)])
        flux_promo2 = self.model.search([('real_id', '=', promo2.id)])
        self.assertEqual(len(flux_promo1), 3)
        self.assertEqual(len(flux_promo2), 3)
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            mapper = work.component(usage='export.mapper')
            checksums_1 = []
            for r in flux_promo1:
                checksums_1.append(
                    mapper.map_record(r).values(alcyon_group_id='buyxgety')[
                        'CheckSum'
                    ]
                )
            self.assertEqual(len(set(checksums_1)), 1)
            checksums_2 = []
            for r in flux_promo2:
                checksums_2.append(
                    mapper.map_record(r).values(alcyon_group_id='buyxgety')[
                        'CheckSum'
                    ]
                )
            self.assertEqual(len(set(checksums_2)), 1)
        self.assertTrue(checksums_1[0] != checksums_2[0])
