# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ESBXMLTestCase


class WSProductStockTestCase(ESBXMLTestCase):

    def setUp(self):
        super(WSProductStockTestCase, self).setUp()
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
            'default_code': 'exportable001',
        })
        self.product2 = self.model.create({
            'name': 'Product2',
            'default_code': 'exportable002',
        })
        self.product3 = self.model.create({
            'name': 'Product3',
            'default_code': 'exportable003',
        })
        self.all_records = self.product1 + self.product2 + self.product3

        self.change_product_qty(self.product1, 20)
        self.change_product_qty(self.product2, 0)
        self.change_product_qty(self.product3, 15)

    def test_message(self):
        backend = self.env['esb.backend'].get_singleton()
        skus = self.all_records.mapped('default_code')
        with backend.work_on('product.product') as work:
            component = work.component('ws.message.product.stock')
            message = component.get_message(skus)
        self.assertXmlEquivalentData(
            message, self.read_test_file('product_stock_ws_1.xml'), 'sku')
