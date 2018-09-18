# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ESBXMLTestCase


class WSProductStockSKUTestCase(ESBXMLTestCase):

    def setUp(self):
        super(WSProductStockSKUTestCase, self).setUp()
        self.setup_records()

    @property
    def model(self):
        return self.env['product.product']

    def change_product_qty(self, product, qty):
        self.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'new_quantity': qty,
        }).change_product_qty()

    def setup_records(self):
        self.product1 = self.model.create({
            'name': 'Product1',
            'default_code': 'Product1',
        })
        self.product2 = self.model.create({
            'name': 'Product2',
            'default_code': 'Product2',
        })
        self.product3 = self.model.create({
            'name': 'Product3',
            'default_code': 'Product3',
        })
        self.all_records = self.product1 + self.product2 + self.product3

        self.change_product_qty(self.product1, 20)
        self.change_product_qty(self.product2, 0)
        self.change_product_qty(self.product3, 15)

    def test_message(self):
        backend = self.env['esb.backend'].get_singleton()
        skus = self.all_records.mapped('default_code')
        with backend.work_on('product.product') as work:
            component = work.component('ws.message.product.stock.sku')
            result = component.get_message(skus)

        product_mapper = {
            'Product1': self.product1,
            'Product2': self.product2,
            'Product3': self.product3
        }

        self.assertEqual(len(result), 3)
        for product_values in result:
            product = product_mapper[product_values['sku']]
            qty = product_values['quantity']
            self.assertEqual(product.immediately_usable_qty, qty)

        # Disable the product 1
        self.product1.sale_ok = False
        backend = self.env['esb.backend'].get_singleton()
        skus = self.all_records.mapped('default_code')
        with backend.work_on('product.product') as work:
            component = work.component('ws.message.product.stock.sku')
            result = component.get_message(skus)
        self.assertEqual(len(result), 2)
