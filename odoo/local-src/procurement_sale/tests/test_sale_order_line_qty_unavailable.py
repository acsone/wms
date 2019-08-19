# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import timedelta

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase, at_install, post_install

_logger = logging.getLogger(__name__)


class TestSaleOrderLineQtyUnavailable(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLineQtyUnavailable, self).setUp()

        self.location_model = self.env['stock.location']
        self.inventory_model = self.env['stock.inventory']
        self.inventory_line_model = self.env['stock.inventory.line']

        self.stock_location = self.location_model.browse(
            self.ref('stock.stock_location_stock')
        )

        self.tax = self.env["account.tax"].create(
            {
                'name': 'Unittest tax',
                'price_include': False,
                'amount_type': 'percent',
                'amount': '0',
            }
        )

        self.p1 = self.env['product.template'].create(
            {
                'name': 'Unittest P1',
                'uom_id': self.ref('product.product_uom_unit'),
                'type': 'product',
            }
        )

        self.partner = self.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '4929752'}
        )

    def _define_product_qty(self, product, quantity):
        self.inventory = self.inventory_model.create(
            {
                'name': 'Unittest Inventory',
                'location_id': self.stock_location.id,
                'filter': 'partial',
            }
        )
        self.inventory.prepare_inventory()

        self.inventory_line_model.create(
            {
                'inventory_id': self.inventory.id,
                'product_id': product.id,
                'location_id': self.stock_location.id,
                'product_qty': quantity,
            }
        )
        self.inventory.action_done()

    @at_install(False)
    @post_install(True)
    def test_01_basic(self):
        # At test beginning, the product immediately usable quantity is 0
        self.assertEqual(
            self.p1.product_variant_ids[0].immediately_usable_qty, 0
        )

        # ****************************************
        # ************ First order ***************
        # ****************************************

        # Create the first sale order with 10 as ordered quantity
        self.sale_1 = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
                'date_order': Datetime.now(),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.product_variant_ids.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 10,
                            'sequence': 1,
                        },
                    )
                ],
            }
        )

        # After the first order (qty = 10), the unavailable quantity is 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        self.assertEqual(
            self.sale_1.order_line[0].current_product_qty_unavailable, 10
        )

        # Confirm the first order

        self.sale_1.action_confirm()

        # After the confirmation of first order (qty = 10),
        # the product immediately usable quantity is -10
        self.env['product.product'].refresh()
        self.env['stock.move'].refresh()
        self.assertEqual(
            self.p1.product_variant_ids[0].immediately_usable_qty, -10
        )
        # After the confirmation of first order (qty = 10),
        # the unavailable quantity is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        self.assertEqual(
            self.sale_1.order_line[0].current_product_qty_unavailable, 10
        )

        # ****************************************
        # ************ Second order **************
        # ****************************************

        # Create the second sale order with 5 as ordered quantity
        self.sale_2 = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
                'date_order': Datetime.to_string(
                    Datetime.from_string(Datetime.now()) + timedelta(hours=1)
                ),
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.product_variant_ids.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 5,
                            'sequence': 1,
                        },
                    )
                ],
            }
        )

        # After the second order (qty = 5), the unavailable quantity is 5
        self.env['product.product'].refresh()
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        self.assertEqual(
            self.sale_2.order_line[0].current_product_qty_unavailable, 5
        )

        # Confirm the second order
        self.sale_2.action_confirm()

        # After the confirmation of second order (qty = 5),
        # the product immediately usable quantity is -15
        self.assertEqual(
            self.p1.product_variant_ids[0].immediately_usable_qty, -15
        )
        # After the confirmation of second order (qty = 5),
        # the unavailable quantity on first order is already 10
        self.sale_1.refresh()
        self.sale_2.refresh()
        self.env['product.product'].refresh()
        self.env['stock.move'].refresh()
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        self.assertEqual(
            self.sale_1.order_line[0].current_product_qty_unavailable, 10
        )
        # After the confirmation of second order (qty = 5),
        # the unavailable quantity is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        self.assertEqual(
            self.sale_2.order_line[0].current_product_qty_unavailable, 5
        )

        # ****************************************
        # ********** Increase the stock **********
        # ****************************************

        self._define_product_qty(self.p1.product_variant_ids[0], 2)
        self.p1.refresh()
        self.sale_1.refresh()
        self.sale_2.refresh()
        self.env['product.product'].refresh()
        self.env['stock.move'].refresh()
        # After the stock increase (qty = 2),
        # the product immediately usable quantity is -13
        self.assertEqual(
            self.p1.product_variant_ids[0].immediately_usable_qty, -13
        )
        # After the stock increase (qty = 2),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 8
        self.assertEqual(
            self.sale_1.order_line[0].current_product_qty_unavailable, 8
        )
        # After the stock increase (qty = 2),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is already 5
        self.assertEqual(
            self.sale_2.order_line[0].current_product_qty_unavailable, 5
        )

        # ****************************************
        # ********** Increase the stock **********
        # ****************************************

        self._define_product_qty(self.p1.product_variant_ids[0], 11)
        self.p1.refresh()

        # After the stock increase (qty = 11),
        # the product immediately usable quantity is -4
        self.assertEqual(
            self.p1.product_variant_ids[0].immediately_usable_qty, -4
        )
        # After the stock increase (qty = 11),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 0
        self.assertEqual(
            self.sale_1.order_line[0].current_product_qty_unavailable, 0
        )
        # After the stock increase (qty = 11),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is now 4
        self.assertEqual(
            self.sale_2.order_line[0].current_product_qty_unavailable, 4
        )

        # ****************************************
        # ********** Increase the stock **********
        # ****************************************

        self._define_product_qty(self.p1.product_variant_ids[0], 15)
        self.p1.refresh()

        # After the stock increase (qty = 15),
        # the product immediately usable quantity is 0
        self.assertEqual(
            self.p1.product_variant_ids[0].immediately_usable_qty, 0
        )
        # After the stock increase (qty = 15),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 0
        self.assertEqual(
            self.sale_1.order_line[0].current_product_qty_unavailable, 0
        )
        # After the stock increase (qty = 11),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is now 0
        self.assertEqual(
            self.sale_2.order_line[0].current_product_qty_unavailable, 0
        )

        # ****************************************
        # ********** Increase the stock **********
        # ****************************************

        self._define_product_qty(self.p1.product_variant_ids[0], 20)
        self.p1.refresh()

        # After the stock increase (qty = 15),
        # the product immediately usable quantity is 5
        self.assertEqual(
            self.p1.product_variant_ids[0].immediately_usable_qty, 5
        )
        # After the stock increase (qty = 15),
        # the unavailable quantity on first order is already 10
        self.assertEqual(self.sale_1.order_line[0].product_qty_unavailable, 10)
        # the current unavailable quantity on first order is now 0
        self.assertEqual(
            self.sale_1.order_line[0].current_product_qty_unavailable, 0
        )
        # After the stock increase (qty = 11),
        # the unavailable quantity on second order is already 5
        self.assertEqual(self.sale_2.order_line[0].product_qty_unavailable, 5)
        # the current unavailable quantity on second order is now 0
        self.assertEqual(
            self.sale_2.order_line[0].current_product_qty_unavailable, 0
        )
