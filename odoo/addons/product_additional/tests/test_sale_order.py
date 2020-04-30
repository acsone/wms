# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestSaleOrder(common.SavepointCase):
    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()

        context = dict(cls.env.context)
        context.update({"tracking_disable": True})
        cls.env = cls.env(context=context)

        # Create partner
        cls.partner = cls.env['res.partner'].create(
            {
                'name': 'Hello World',
                'ref': '95739887576',
                'supplier_promotion_sale_allowed': True,
            }
        )

        cls.supplier = cls.env['res.partner'].create(
            {'name': 'Supplier', 'ref': '875893929', 'supplier': True}
        )

        # Create the main product
        cls.main_product = cls.env['product.product'].create(
            {
                'name': 'Main product',
                'default_code': '1234567',
                'tracking': 'lot',
                'list_price': 100,
                'type': 'product',
            }
        )

        # Create the sale order
        cls.sale_order = cls.env['sale.order'].create(
            {
                'partner_id': cls.partner.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': cls.main_product.name,
                            'product_id': cls.main_product.id,
                            'product_uom': cls.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 10,
                            'sequence': 1,
                        },
                    )
                ],
            }
        )

    def test_only_allowed_customer(self):
        """Check free products are not given to everyone.

        Customer who are not entitled to supplier promotions should
        not receive the free products.
        """
        self.partner.supplier_promotion_sale_allowed = False
        self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'product_tmpl_id': self.main_product.product_tmpl_id.id,
                'product_code': '123456',
                'delay': 1,
                'ratio_main_product': 3,
                'ratio_promotional_product': 1,
            }
        )
        # Flag on sale order to give or not supplier promotions is set on
        # create and with onchanges
        so = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.main_product.name,
                            'product_id': self.main_product.id,
                            'product_uom': self.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 10,
                            'sequence': 1,
                        },
                    )
                ],
            }
        )
        self.assertEqual(len(self.sale_order.order_line), 1)
        so.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 1)

    def test_action_confirm_1(self):
        """
        Add a simple supplier info (ratio 3/1) without date or min quantity
        :return:
        """
        self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'product_tmpl_id': self.main_product.product_tmpl_id.id,
                'product_code': '123456',
                'delay': 1,
                'ratio_main_product': 3,
                'ratio_promotional_product': 1,
            }
        )
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 2)
        # Check main line
        main_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 10.0
        )
        self.assertEqual(len(main_line), 1)
        # Check promotional line
        promotional_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 3.0
        )
        self.assertEqual(len(promotional_line), 1)
        # check that sequences are correct
        self.assertEqual(main_line.sequence, 1)
        self.assertEqual(promotional_line.sequence, 2)

    def test_action_confirm_2(self):
        """
        Add the first supplier info (ratio 3/1) and a second supplier info
        (ratio 2/1) with a min quantity
        :return:
        """
        self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'product_tmpl_id': self.main_product.product_tmpl_id.id,
                'product_code': '123456',
                'delay': 1,
                'ratio_main_product': 3,
                'ratio_promotional_product': 1,
                'date_start': fields.Date.today(),
                'date_end': fields.Date.today(),
            }
        )
        self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'product_tmpl_id': self.main_product.product_tmpl_id.id,
                'product_code': '123456',
                'min_qty_sale': 5,
                'delay': 1,
                'ratio_main_product': 2,
                'ratio_promotional_product': 1,
                'date_start': fields.Date.today(),
                'date_end': fields.Date.today(),
            }
        )
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 2)
        # Check main line
        main_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 10.0
        )
        self.assertEqual(len(main_line), 1)
        # Check promotional line
        promotional_line = self.sale_order.order_line.filtered(
            lambda line: line.product_uom_qty == 5.0
        )
        self.assertEqual(len(promotional_line), 1)
        # check that sequences are correct
        self.assertEqual(main_line.sequence, 1)
        self.assertEqual(promotional_line.sequence, 2)

    def test_action_confirm_3(self):
        """
        Create a supplier info with a expired date_start and date_end
        :return:
        """
        self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'product_tmpl_id': self.main_product.product_tmpl_id.id,
                'product_code': '123456',
                'delay': 1,
                'ratio_main_product': 2,
                'ratio_promotional_product': 1,
                'date_start': '2017-01-01',
                'date_end': '2017-06-30',
            }
        )
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 1)

    def test_action_draft_1(self):
        """
        Confirm a sale order and reset the state to draft
        :return:
        """
        self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'product_tmpl_id': self.main_product.product_tmpl_id.id,
                'product_code': '123456',
                'delay': 1,
                'ratio_main_product': 3,
                'ratio_promotional_product': 1,
            }
        )
        self.assertEqual(len(self.sale_order.order_line), 1)

        self.sale_order.action_confirm()
        self.assertEqual(len(self.sale_order.order_line), 2)

        self.sale_order.action_cancel()
        self.sale_order.action_draft()
        self.assertEqual(len(self.sale_order.order_line), 1)

    def test_sequence_on_line_with_additional_product(self):
        """Check the position of free products in sale order line.

        The free products added at confirmation order should be listed
        just after the corresponding paid products.
        """
        # Create a product without promotion
        self.product_2 = self.env['product.product'].create(
            {
                'name': 'Product 2',
                'default_code': '984928374',
                'tracking': 'lot',
                'list_price': 100,
                'type': 'product',
            }
        )
        # Add a free product on the main product
        self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'product_tmpl_id': self.main_product.product_tmpl_id.id,
                'product_code': '123456',
                'delay': 1,
                'ratio_main_product': 10,
                'ratio_promotional_product': 1,
            }
        )
        # Create the sale order without setting a sequence on sale order lines
        self.so_2 = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.main_product.name,
                            'product_id': self.main_product.id,
                            'product_uom': self.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 10,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.product_2.name,
                            'product_id': self.product_2.id,
                            'product_uom': self.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 3,
                        },
                    ),
                ],
            }
        )
        self.so_2.action_confirm()
        self.assertEqual(len(self.so_2.order_line), 3)
        # Check the sequence on the product and its promotion
        main_line = self.so_2.order_line.filtered(
            lambda line: line.product_uom_qty == 10.0
        )
        self.assertEqual(main_line.sequence, 1)
        promotional_line = self.so_2.order_line.filtered(
            lambda line: line.product_uom_qty == 1.0
        )
        self.assertEqual(promotional_line.sequence, 2)
