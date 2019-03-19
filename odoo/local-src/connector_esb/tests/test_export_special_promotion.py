# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from .common import ESBXMLTestCase


class ExportSpecialPromotionTestCase(ESBXMLTestCase):
    def setUp(self):
        super(ExportSpecialPromotionTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref(
            'connector_esb.esb_timestamp_special_promotion'
        )

    @property
    def model(self):
        return self.env['product.supplierinfo.esbflux']

    def setup_records(self):
        self.model.search([(1, '=', 1)]).unlink()
        # Create 2 products
        self.p1 = self.env['product.template'].create(
            {'name': 'Unittest P1', 'default_code': '0001'}
        )
        self.p2 = self.env['product.template'].create(
            {'name': 'Unittest P2', 'default_code': '0002'}
        )
        # Create a supplier
        self.supplier1 = self.env['res.partner'].create(
            {
                'ref': '123123',
                'name': 'Joe',
                'street': 'Chemin des Pins, 23',
                'street2': '',
                'zip': '1010',
                'city': 'Lausanne',
                'country_id': 44,
                'phone': '021123123',
                'fax': '021121212',
                'email': 'joe@ch.ch',
                'supplier': True,
            }
        )
        self.weeks_ago = datetime.today() - timedelta(weeks=3)
        self.weeks_fromnow = datetime.today() + timedelta(weeks=3)
        # Current promotion
        self.psi1 = self.model.create(
            {
                'product_tmpl_id': self.p1.id,
                'discount_sale': 5,
                'date_start': self.weeks_ago.strftime('%Y-%m-%d'),
                'date_end': self.weeks_fromnow.strftime('%Y-%m-%d'),
                'flux': 'specialpromotion',
                'action': 'create',
            }
        )
        # Obsolete promotion, it is in the past
        self.psi2 = self.model.create(
            {
                'product_tmpl_id': self.p2.id,
                'discount_sale': 15,
                'date_start': '2017-07-31',
                'date_end': '2017-08-31',
                'flux': 'specialpromotion',
                'action': 'create',
            }
        )
        # Bad promotion no discount
        self.psi3 = self.model.create(
            {
                'product_tmpl_id': self.p1.id,
                'discount_sale': 0,
                'date_start': self.weeks_ago.strftime('%Y-%m-%d'),
                'date_end': self.weeks_fromnow.strftime('%Y-%m-%d'),
                'flux': 'specialpromotion',
                'action': 'create',
            }
        )

    def test_mapper(self):
        """ Testing mapper"""
        rec = self.psi1
        expected = {
            'Sku': u'0001',
            'Percent1': '5.00',
            'Percent2': '0',
            'StartDate': self.weeks_ago.strftime('%Y%m%d'),
            'EndDate': self.weeks_fromnow.strftime('%Y%m%d'),
            'AlcyonGroupId': '100',
            'Action': 'Create',
            'CheckSum': ''.join([str(rec.real_id), '100', 'special']),
        }
        self.timestamp.writer = 'local'
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            mapper = work.component(usage='export.mapper')
            self.assertDictEqual(
                mapper.map_record(rec).values(alcyon_group_id='100'), expected
            )

    def test_domain(self):
        """Test we get the correct items"""
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage='record.exporter.cron')
            items = exporter.get_items(None)
            self.assertEqual(len(items), 1)

    def test_checksum(self):
        """Check checksum correctness.

        The checksum for different action of a promotion have to be the same.
        The checksum for action on different promotion must be different.
        """
        promo1 = self.env['product.supplierinfo'].create(
            {
                'name': self.supplier1.id,
                'product_tmpl_id': self.p2.id,
                'discount_sale': 1,
                'date_start': '2019-01-30',
                'date_end': '2019-03-30',
            }
        )
        promo1.discount_sale = 3
        promo2 = self.env['product.supplierinfo'].create(
            {
                'name': self.supplier1.id,
                'product_tmpl_id': self.p2.id,
                'discount_sale': 9,
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
                    mapper.map_record(r).values(alcyon_group_id='special')[
                        'CheckSum'
                    ]
                )
            self.assertEqual(len(set(checksums_1)), 1)
            checksums_2 = []
            for r in flux_promo2:
                checksums_2.append(
                    mapper.map_record(r).values(alcyon_group_id='special')[
                        'CheckSum'
                    ]
                )
            self.assertEqual(len(set(checksums_2)), 1)
        self.assertTrue(checksums_1[0] != checksums_2[0])
