# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestStockPicking(common.TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestStockPicking, self).setUp()

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

        # Create the sale order
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.main_product.name,
                    'product_id': self.main_product.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })

    def test_action_confirm_1(self):
        """
        Add a simple supplier info (ratio 3/1) without date or min quantity
        :return:
        """
        self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'product_tmpl_id': self.main_product.product_tmpl_id.id,
            'product_code': '123456',
            'delay': 1,
            'ratio_main_product': 3,
            'ratio_promotional_product': 1,
        })
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 2)
        # Check main line
        main_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 10.0)
        self.assertEqual(len(main_line), 1)
        # Check promotional line
        promotional_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 3.0)
        self.assertEqual(len(promotional_line), 1)

    def test_action_confirm_2(self):
        """
        Add the first supplier info (ratio 3/1) and a second supplier info
        (ratio 2/1) with a min quantity
        :return:
        """
        self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'product_tmpl_id': self.main_product.product_tmpl_id.id,
            'product_code': '123456',
            'delay': 1,
            'ratio_main_product': 3,
            'ratio_promotional_product': 1,
        })
        self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'product_tmpl_id': self.main_product.product_tmpl_id.id,
            'product_code': '123456',
            'min_qty_sale': 5,
            'delay': 1,
            'ratio_main_product': 2,
            'ratio_promotional_product': 1,
        })
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 2)
        # Check main line
        main_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 10.0)
        self.assertEqual(len(main_line), 1)
        # Check promotional line
        promotional_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 5.0)
        self.assertEqual(len(promotional_line), 1)

    def test_action_confirm_3(self):
        """
        Create a supplier info with a expired date_start and date_end
        :return:
        """
        self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'product_tmpl_id': self.main_product.product_tmpl_id.id,
            'product_code': '123456',
            'delay': 1,
            'ratio_main_product': 2,
            'ratio_promotional_product': 1,
            'date_start': '2017-01-01',
            'date_end': '2017-06-30',
        })
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 1)

    def test_action_draft_1(self):
        """
        Confirm a sale order and reset the state to draft
        :return:
        """
        self.env['product.supplierinfo'].create({
            'name': self.supplier.id,
            'product_tmpl_id': self.main_product.product_tmpl_id.id,
            'product_code': '123456',
            'delay': 1,
            'ratio_main_product': 3,
            'ratio_promotional_product': 1,
        })
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 2)

        self.sale_order.action_cancel()
        self.sale_order.action_draft()
        self.assertEqual(len(self.sale_order.order_line), 1)
