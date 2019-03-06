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
        self.env['stock.change.product.qty'].create(
            {'product_id': product.id, 'new_quantity': qty}
        ).change_product_qty()

    def setup_records(self):
        active = self.env.ref('specific_purchase.product_state_a')
        active.esb_ref = 'A'
        discontinued = self.env.ref('specific_purchase.product_state_d')
        discontinued.esb_ref = 'D'
        self.product1 = self.model.create(
            {
                'name': 'Product1',
                'default_code': 'exportable001',
                'state_id': active.id,
            }
        )
        self.product2 = self.model.create(
            {
                'name': 'Product2',
                'default_code': 'exportable002',
                'state_id': discontinued.id,
            }
        )
        self.product3 = self.model.create(
            {
                'name': 'Product3',
                'default_code': 'exportable003',
                'state_id': active.id,
            }
        )
        self.all_records = self.product1 + self.product2 + self.product3

        self.change_product_qty(self.product1, 20)
        self.change_product_qty(self.product2, 0)
        self.change_product_qty(self.product3, 15)

        self.customer = self.env['res.partner'].create(
            {
                'ref': '123456',
                'name': 'Joe',
                'street': 'Chemin des Pins, 23',
                'street2': '',
                'zip': '1010',
                'city': 'Lausanne',
                'country_id': 44,
                'phone': '021123123',
                'fax': '021121212',
                'email': 'joe@ch.ch',
            }
        )
        # Confirm a sale order on product 1 to change the available stock
        # But not the physical
        self.so1 = self.env['sale.order'].create(
            {
                'partner_id': self.customer.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.product1.name,
                            'product_id': self.product1.id,
                            'product_uom': 1,
                            'product_uom_qty': 5,
                        },
                    )
                ],
            }
        )
        self.so1.action_confirm()

    def test_message(self):
        backend = self.env['esb.backend'].get_singleton()
        skus = self.all_records.mapped('default_code')
        with backend.work_on('product.product') as work:
            component = work.component('ws.message.product.stock')
            message = component.get_message(skus)
        self.assertXmlEquivalentData(
            message, self.read_test_file('product_stock_ws_1.xml'), 'sku'
        )
