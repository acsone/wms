# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class ProductSupplierInfoEsbFluxPurgeTestCase(TransactionCase):
    def setUp(self):
        super(ProductSupplierInfoEsbFluxPurgeTestCase, self).setUp()
        self.model = self.env['product.supplierinfo.esbflux']

    def create_action(self, action, real_id):
        return self.model.create({'action': action, 'real_id': real_id})

    def print_actions(self, rs):
        print('|-----')
        for r in rs:
            print('{}: {}'.format(r.action, r.real_id))
        print('-----|')

    def test_start_finish_by_create(self):
        """Only keep the last create"""
        rs = self.model.browse()
        rs |= self.create_action('create', 1)
        rs |= self.create_action('create', 2)
        rs |= self.create_action('delete', 2)
        rs |= self.create_action('delete', 1)
        m1 = self.create_action('create', 1)
        rs |= m1
        new_rs = rs.remove_duplicate_actions()
        self.assertTrue(m1 in new_rs)
        self.assertEqual(len(new_rs), 1)

    def test_start_finish_by_delete(self):
        """Only keep the first delete"""
        rs = self.model.browse()
        m1 = self.create_action('delete', 1)
        rs |= m1
        m2 = self.create_action('create', 2)
        rs |= m2
        rs |= self.create_action('create', 3)
        m3 = self.create_action('create', 4)
        rs |= m3
        rs |= self.create_action('delete', 3)
        rs |= self.create_action('create', 1)
        rs |= self.create_action('delete', 1)
        new_rs = rs.remove_duplicate_actions()
        self.assertTrue(m1 in new_rs)
        self.assertTrue(m2 in new_rs)
        self.assertTrue(m3 in new_rs)
        self.assertEqual(len(new_rs), 3)

    def test_start_create_finish_delete(self):
        """Keep nothing """
        rs = self.model.browse()
        rs |= self.create_action('create', 1)
        m2 = self.create_action('create', 2)
        rs |= m2
        rs |= self.create_action('create', 3)
        m4 = self.create_action('create', 4)
        rs |= m4
        rs |= self.create_action('delete', 1)
        rs |= self.create_action('create', 1)
        rs |= self.create_action('delete', 1)
        rs |= self.create_action('delete', 3)
        new_rs = rs.remove_duplicate_actions()
        self.assertTrue(m2 in new_rs)
        self.assertTrue(m4 in new_rs)
        self.assertEqual(len(new_rs), 2)

    def test_start_delete_finish_create(self):
        "Keep both"
        rs = self.model.browse()
        m1 = self.create_action('delete', 1)
        rs |= m1
        m3 = self.create_action('delete', 2)
        rs |= m3
        rs |= self.create_action('create', 3)
        m4 = self.create_action('create', 4)
        rs |= m4
        rs |= self.create_action('create', 1)
        rs |= self.create_action('delete', 1)
        m2 = self.create_action('create', 1)
        rs |= m2
        rs |= self.create_action('delete', 3)
        new_rs = rs.remove_duplicate_actions()
        self.assertTrue(m1 in new_rs)
        self.assertTrue(m4 in new_rs)
        self.assertTrue(m2 in new_rs)
        self.assertTrue(m3 in new_rs)
        self.assertEqual(len(new_rs), 4)
