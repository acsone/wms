# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, at_install, post_install


class TestProductCategoryExpiredTimes(TransactionCase):
    def setUp(self):
        super(TestProductCategoryExpiredTimes, self).setUp()
        self.category_model = self.env['product.category']
        self.product_model = self.env['product.product']

        self.category = self.category_model.create(
            {'name': 'Unittest category'}
        )
        self.product = self.product_model.create(
            {
                'name': 'Unittest product',
                'type': 'product',
                'categ_id': self.category.id,
            }
        )

    @post_install(True)
    @at_install(False)
    def test_1_related_fields(self):
        self.assertFalse(self.category.use_time)
        self.assertFalse(self.category.life_time)
        self.assertFalse(self.category.alert_time)
        self.assertFalse(self.category.removal_time)

        self.assertFalse(self.product.use_time)
        self.assertFalse(self.product.life_time)
        self.assertFalse(self.product.alert_time)
        self.assertFalse(self.product.removal_time)

        self.category.write(
            {'use_time': 1, 'life_time': 2, 'alert_time': 3, 'removal_time': 4}
        )
        self.assertEqual(self.category.use_time, 1)
        self.assertEqual(self.category.life_time, 2)
        self.assertEqual(self.category.alert_time, 3)
        self.assertEqual(self.category.removal_time, 4)

        self.assertEqual(self.product.use_time, 1)
        self.assertEqual(self.product.life_time, 2)
        self.assertEqual(self.product.alert_time, 3)
        self.assertEqual(self.product.removal_time, 4)

        self.product.write(
            {
                'use_time': 10,
                'life_time': 20,
                'alert_time': 30,
                'removal_time': 40,
            }
        )
        self.assertEqual(self.category.use_time, 10)
        self.assertEqual(self.category.life_time, 20)
        self.assertEqual(self.category.alert_time, 30)
        self.assertEqual(self.category.removal_time, 40)

        self.assertEqual(self.product.use_time, 10)
        self.assertEqual(self.product.life_time, 20)
        self.assertEqual(self.product.alert_time, 30)
        self.assertEqual(self.product.removal_time, 40)
