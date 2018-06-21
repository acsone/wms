# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestPurchaseOrder(common.TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()

        # Create partner
        self.partner = self.env['res.partner'].create({
            'name': 'Hello World',
        })

        self.supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })

        # Create the main product
        self.main_product = self.env['product.product'].create({
            'name': 'Main product',
            'default_code': '1234567',
            'tracking': 'lot',
            'list_price': 100,
            'type': 'product',
        })

        self.additional_product = self.env['product.product'].create({
            'name': 'Second product',
            'default_code': '987654321',
            'tracking': 'none',
            'list_price': 20,
            'type': 'product',
        })

        # Create the purchase_order
        self.purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.main_product.name,
                    'product_id': self.main_product.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_qty': 12,
                    'sequence': 1,
                    'price_unit_base': 100,
                    'date_planned': fields.Datetime.now(),
                }),
            ],
        })

    def test_action_confirm_1(self):
        """
        Confirm a purchase order without additional product
        :return:
        """
        self.assertEqual(len(self.purchase_order.order_line), 1)

        self.purchase_order.button_confirm()
        self.assertEqual(len(self.purchase_order.order_line), 1)

    def test_action_confirm_2(self):
        """
        Set an additional product with ratio (5/2) and cancel this purchase
        order
        :return:
        """
        self.main_product.write({
            'ratio_main_product': 5,
            'ratio_additional_product': 2,
            'additional_product_id': self.additional_product.id
        })
        self.assertEqual(len(self.purchase_order.order_line), 1)

        self.purchase_order.button_confirm()
        self.assertEqual(len(self.purchase_order.order_line), 2)
        # Check main line
        main_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 12.0)
        self.assertEqual(len(main_line), 1)
        self.assertEqual(main_line.price_unit_base, 100.0)
        # Check promotional line
        additional_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 4.0)
        self.assertEqual(len(additional_line), 1)
        self.assertEqual(additional_line.price_unit_base, 0.0)

        # Cancel the PO
        self.purchase_order.button_draft()
        self.assertEqual(len(self.purchase_order.order_line), 1)
        # Check main line
        main_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 12.0)
        self.assertEqual(len(main_line), 1)
        # Check promotional line
        additional_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_qty == 4.0)
        self.assertEqual(len(additional_line), 0)
