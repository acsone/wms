# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase, post_install, at_install


class TestStockProductionLotLifeDates(TransactionCase):

    def setUp(self):
        super(TestStockProductionLotLifeDates, self).setUp()
        self.category_model = self.env['product.category']
        self.product_model = self.env['product.product']
        self.production_lot_model = self.env['stock.production.lot']
        self.stock_config_settings_model = self.env['stock.config.settings']

        self.category = self.category_model.create({
            'name': 'Unittest category',
        })
        self.product = self.product_model.create({
            'name': 'Unittest product',
            'type': 'product',
            'categ_id': self.category.id,
            'use_time': 0,
            'life_time': 1,
            'alert_time': 2,
            'removal_time': 3,
        })
        self.production_lot = self.production_lot_model.create({
            'name': '000001',
            'product_id': self.product.id,
        })

        self.category_2 = self.category_model.create({
            'name': 'Unittest category 2',
        })
        self.product_2 = self.product_model.create({
            'name': 'Unittest product 2',
            'type': 'product',
            'categ_id': self.category_2.id,
            'use_time': -3,
            'life_time': -2,
            'alert_time': -1,
            'removal_time': 0,
        })
        self.production_lot_2 = self.production_lot_model.create({
            'name': '000001',
            'product_id': self.product_2.id,
        })

    @post_install(True)
    @at_install(False)
    def test_1_onchange_use_date(self):
        for production_lot in [self.production_lot, self.production_lot_2]:
            for base_date in [None, 'alert', 'life', 'removal', 'use']:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                settings = self.stock_config_settings_model.create({
                    'production_lot_base_date': base_date
                })
                settings.execute()
                production_lot.use_date = '2016-12-23 10:00:00'
                production_lot.onchange_use_date()
                self.assertEqual(
                    production_lot.use_date,
                    '2016-12-23 10:00:00'
                )
                self.assertEqual(
                    production_lot.life_date,
                    '2016-12-24 10:00:00' if base_date == 'use' else False
                )
                self.assertEqual(
                    production_lot.alert_date,
                    '2016-12-25 10:00:00' if base_date == 'use' else False
                )
                self.assertEqual(
                    production_lot.removal_date,
                    '2016-12-26 10:00:00' if base_date == 'use' else False
                )
                # Check the onchange not fails with no value
                production_lot.use_date = False
                production_lot.onchange_use_date()

    @post_install(True)
    @at_install(False)
    def test_2_onchange_life_date(self):
        for production_lot in [self.production_lot, self.production_lot_2]:
            for base_date in [None, 'alert', 'life', 'removal', 'use']:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                settings = self.stock_config_settings_model.create({
                    'production_lot_base_date': base_date
                })
                settings.execute()
                production_lot.life_date = '2016-12-23 10:00:00'
                production_lot.onchange_life_date()
                self.assertEqual(
                    production_lot.use_date,
                    '2016-12-22 10:00:00' if base_date == 'life' else False
                )
                self.assertEqual(
                    production_lot.life_date,
                    '2016-12-23 10:00:00'
                )
                self.assertEqual(
                    production_lot.alert_date,
                    '2016-12-24 10:00:00' if base_date == 'life' else False
                )
                self.assertEqual(
                    production_lot.removal_date,
                    '2016-12-25 10:00:00' if base_date == 'life' else False
                )
                # Check the onchange not fails with no value
                production_lot.life_date = False
                production_lot.onchange_life_date()

    @post_install(True)
    @at_install(False)
    def test_3_onchange_alert_date(self):
        for production_lot in [self.production_lot, self.production_lot_2]:
            for base_date in [None, 'alert', 'life', 'removal', 'use']:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                settings = self.stock_config_settings_model.create({
                    'production_lot_base_date': base_date
                })
                settings.execute()
                production_lot.alert_date = '2016-12-23 10:00:00'
                production_lot.onchange_alert_date()
                self.assertEqual(
                    production_lot.use_date,
                    '2016-12-21 10:00:00' if base_date == 'alert' else False
                )
                self.assertEqual(
                    production_lot.life_date,
                    '2016-12-22 10:00:00' if base_date == 'alert' else False
                )
                self.assertEqual(
                    production_lot.alert_date,
                    '2016-12-23 10:00:00'
                )
                self.assertEqual(
                    production_lot.removal_date,
                    '2016-12-24 10:00:00' if base_date == 'alert' else False
                )
                # Check the onchange not fails with no value
                production_lot.alert_date = False
                production_lot.onchange_alert_date()

    @post_install(True)
    @at_install(False)
    def test_4_onchange_removal_date(self):
        for production_lot in [self.production_lot, self.production_lot_2]:
            for base_date in [None, 'alert', 'life', 'removal', 'use']:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                settings = self.stock_config_settings_model.create({
                    'production_lot_base_date': base_date
                })
                settings.execute()
                production_lot.removal_date = '2016-12-23 10:00:00'
                production_lot.onchange_removal_date()
                self.assertEqual(
                    production_lot.use_date,
                    '2016-12-20 10:00:00' if base_date == 'removal' else False
                )
                self.assertEqual(
                    production_lot.life_date,
                    '2016-12-21 10:00:00' if base_date == 'removal' else False
                )
                self.assertEqual(
                    production_lot.alert_date,
                    '2016-12-22 10:00:00' if base_date == 'removal' else False
                )
                self.assertEqual(
                    production_lot.removal_date,
                    '2016-12-23 10:00:00'
                )
                # Check the onchange not fails with no value
                production_lot.removal_date = False
                production_lot.onchange_removal_date()
