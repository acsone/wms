# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from .common import ESBXMLTestCase


class ExportPromotionAlcyonTestCase(ESBXMLTestCase):
    def setUp(self):
        super(ExportPromotionAlcyonTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref(
            'connector_esb.esb_timestamp_promotion_alcyon'
        )
        self.timestamp.writer = 'local'

    @property
    def model(self):
        return self.env['product.pricelist.item']

    def setup_records(self):
        # Create 2 products
        self.p1 = self.env['product.product'].create(
            {'name': 'Unittest P1', 'default_code': '0001'}
        )
        self.p2 = self.env['product.product'].create(
            {'name': 'Unittest P2', 'default_code': '0002'}
        )
        self.p3 = self.env['product.product'].create(
            {'name': 'Unittest P3', 'default_code': '0003'}
        )
        # Could be changed when export-product is merged ?
        self.ali = self.env['product.price.category'].create({'name': 'ALI'})
        self.alg = self.env['product.price.category'].create({'name': 'ALG'})
        # Create a new pricelist with percentage discount on the product 1
        self.discount_pricelist_1 = self.env['product.pricelist'].create(
            {
                'name': 'Discount list 1',
                'esb_ref': 'Ref123',
                'item_ids': [
                    (
                        0,
                        False,
                        {
                            'applied_on': '2b_product_price_category',
                            'product_id': self.p1.id,
                            'compute_price': 'percentage',
                            'percent_price': 5,
                            'price_category_id': self.ali.id,
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            'applied_on': '3_global',
                            'product_id': self.p2.id,
                            'compute_price': 'percentage',
                            'percent_price': 8,
                            'price_category_id': '',
                        },
                    ),
                    (
                        0,
                        False,
                        {
                            'applied_on': '2b_product_price_category',
                            'product_id': self.p3.id,
                            'compute_price': 'percentage',
                            'percent_price': 0,
                            'price_category_id': self.alg.id,
                        },
                    ),
                ],
            }
        )

    def test_filename(self):
        self.check_filename('AlcyonPromotion_{0}.xml')

    def test_mapper_applied_on_2b(self):
        """ Testing mapper on 2b_product_price_category """
        expected = {
            'AlcyonGroupId': 'Ref123',
            'Percent1': '5.00',
            'Percent2': '0',
            'ProductType': 'ALI',
        }
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            mapper = work.component(usage='export.mapper')
            rec = self.discount_pricelist_1.item_ids.filtered(
                lambda r: r.product_id.id == self.p1.id
            )[0]
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_mapper_applied_on_3(self):
        """ Testing mapper on 3_global """
        expected = {
            'AlcyonGroupId': 'Ref123',
            'Percent1': '8.00',
            'Percent2': '0',
            'ProductType': '       ',
        }
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            mapper = work.component(usage='export.mapper')
            rec = self.discount_pricelist_1.item_ids.filtered(
                lambda r: r.applied_on == '3_global'
            )[0]
            self.assertDictEqual(mapper.map_record(rec).values(), expected)

    def test_getitems(self):
        """If both percent are 0 do not include entry

        And the percent 2 is always zero by the way
        """
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage='record.exporter.cron')
            items = exporter.get_items(None)
            self.assertEqual(
                len(items), len(self.discount_pricelist_1.item_ids) - 1
            )

    def test_export(self):
        """ Make a full export check with existing xml file"""
        with self.backend.work_on(
            self.model._name, timestamp=self.timestamp
        ) as work:
            exporter = work.component(usage='record.exporter.cron')
            respath = exporter.run()
            self.addCleanup(os.remove, respath)
            with open(respath, 'r') as result_file:
                result = result_file.read()
            self.assertXmlEquivalentData(
                result,
                self.read_test_file('promotion_alcyon_1.xml'),
                'ProductType',
            )
