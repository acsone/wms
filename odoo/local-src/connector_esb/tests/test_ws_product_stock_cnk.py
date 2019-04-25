# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ESBXMLTestCase


class WSProductStockCNKTestCase(ESBXMLTestCase):
    def setUp(self):
        super(WSProductStockCNKTestCase, self).setUp()
        self.setup_records()

    @property
    def model(self):
        return self.env['product.product']

    def change_product_qty(self, product, qty):
        self.env['stock.change.product.qty'].create(
            {'product_id': product.id, 'new_quantity': qty}
        ).change_product_qty()

    def setup_records(self):
        self.product1 = self.model.create(
            {
                'name': 'Product1',
                'default_code': 'Product1',
                'cnk_code': '000015',
            }
        )
        self.product2 = self.model.create(
            {
                'name': 'Product2',
                'default_code': 'Product2',
                'cnk_code': '000048',
            }
        )
        self.product3 = self.model.create(
            {
                'name': 'Product3',
                'default_code': 'Product3',
                'cnk_code': '000115',
            }
        )
        self.product4 = self.model.create(
            {
                'name': 'Product4',
                'default_code': 'Product4',
                'cnk_code': '000225',
                'sale_ok': False,
                'veterinary_only': True,
                'categ_id': self.env.ref(
                    'specific_data.product_categ_vet_belges'
                ).id,
            }
        )
        self.product5 = self.model.create(
            {
                'name': 'Product5',
                'default_code': 'Product5',
                'cnk_code': '000335',
                'sale_ok': False,
                'veterinary_only': True,
                'categ_id': self.env.ref(
                    'specific_data.product_categ_psychotropes_25'
                ).id,
            }
        )
        self.all_records = (
            self.product1
            + self.product2
            + self.product3
            + self.product4
            + self.product5
        )

        self.change_product_qty(self.product1, 20)
        self.change_product_qty(self.product2, 0)
        self.change_product_qty(self.product3, 15)

    def test_message(self):
        backend = self.env['esb.backend'].get_singleton()
        cnks = self.all_records.mapped('cnk_code')
        with backend.work_on('product.product') as work:
            component = work.component('ws.message.product.stock.cnk')
            result = component.get_message(cnks)

        product_mapper = {
            '000015': self.product1,
            '000048': self.product2,
            '000115': self.product3,
        }

        self.assertEqual(len(result), 3)
        for product_values in result:
            product = product_mapper[product_values['cnk']]
            qty = product_values['quantity']
            pid = product_values['pid']
            self.assertEqual(product.immediately_usable_qty, qty)
            self.assertEqual(product.default_code, pid)

        # Disable the product 1
        self.product1.sale_ok = False
        backend = self.env['esb.backend'].get_singleton()
        cnks = self.all_records.mapped('cnk_code')
        with backend.work_on('product.product') as work:
            component = work.component('ws.message.product.stock.cnk')
            result = component.get_message(cnks)
        self.assertEqual(len(result), 2)

    def test_message_for_newpharma(self):
        newpharma_user = self.env['res.users'].create(
            {
                'login': 'test_newpharma',
                'name': 'Test NewPharma',
                'is_for_newpharma': True,
            }
        )
        # Set the product 2 to veterinary_only so should not be picked up
        self.product2.veterinary_only = True
        # Activate the belgium medocs, that should be included
        self.product4.sale_ok = True
        self.product5.sale_ok = True

        backend = self.env['esb.backend'].get_singleton()
        cnks = self.all_records.mapped('cnk_code')

        # Add fake CNK
        cnks.append('00000001')

        with backend.with_context(uid=newpharma_user.id).work_on(
            'product.product'
        ) as work:
            component = work.component('ws.message.product.stock.cnk')
            result = component.get_message(cnks)

        product_mapper = {
            '000015': self.product1,
            '000048': self.product2,
            '000115': self.product3,
            '000225': self.product4,
            '000335': self.product5,
        }

        self.assertEqual(len(result), 4)
        for product_values in result:
            product = product_mapper[product_values['cnk']]
            qty = product_values['quantity']
            pid = product_values['pid']
            self.assertEqual(product.immediately_usable_qty, qty)
            self.assertEqual(product.default_code, pid)
