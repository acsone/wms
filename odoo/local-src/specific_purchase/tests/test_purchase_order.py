# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from odoo import fields


class TestPurchaseOrder(common.TransactionCase):

    def test_get_next_scheduled_date(self):
        """
        Calendar:
        - 31 december 2017: Saturday
        - 1 january 2017: Sunday
        - 2 january 2017: Monday
        - 3 january 2017: Tuesday
        - 4 january 2017: Wednesday
        - 5 january 2017: Thursday
        - 6 january 2017: Friday
        - 7 january 2017: Saturday
        - 8 january 2017: Sunday
        :return:
        """
        # Set the default lead time to 3 days
        self.env['ir.config_parameter'].set_param('purchase.lead_time', '0')

        # Create a bank holiday
        bank_holiday = self.env['bank.holiday']
        bank_holiday.create({
            'name': '2 January',
            'date': '2017-01-02'
        })
        bank_holiday.create({
            'name': '9 January',
            'date': '2017-01-09'
        })

        pol = self.env['purchase.order.line']

        partner = self.env['res.partner'].create({
            'name': 'Partner Test'
        })
        seller = self.env['product.supplierinfo'].create({
            'name': partner.id,
            'min_qty': 0,
            'price': 100,
            'delay': 3
        })

        # Try different date with a lead time of 3 days defined on the seller
        date_planned = pol.get_next_scheduled_date(seller, '2016-12-31')
        self.assertEqual(date_planned, '2017-01-05 00:00:00')

        date_planned = pol.get_next_scheduled_date(seller, '2017-01-02')
        self.assertEqual(date_planned, '2017-01-05 00:00:00')

        date_planned = pol.get_next_scheduled_date(seller, '2017-01-03')
        self.assertEqual(date_planned, '2017-01-06 00:00:00')

        date_planned = pol.get_next_scheduled_date(seller, '2017-01-06')
        self.assertEqual(date_planned, '2017-01-12 00:00:00')

        # Try with an empty seller and use the default lead time
        empty_seller = self.env['product.supplierinfo']
        date_planned = pol.get_next_scheduled_date(empty_seller, '2016-12-31')
        self.assertEqual(date_planned, '2016-12-31 00:00:00')

    def test_unit_price(self):
        """
        The field unit_price has been changed
        to take in count discounts from Alcyon.
        This modification modify a very important field.
        It's why need to do some unit tests.
        :return:
        """

        supplier = self.env['res.partner'].create({
            'name': 'Supplier',
            'supplier': True,
        })
        product = self.env['product.product'].create({
            'name': 'Product 1',
        })

        po = self.env['purchase.order'].create({
            'partner_id': supplier.id,
            'date_order': fields.Datetime.now(),
            'date_planned': fields.Datetime.now(),
        })

        # Create a line with price_unit (old style)
        # Keep only for compatibility
        po.order_line.create({
            'order_id': po.id,
            'product_id': product.id,
            'name': product.name,
            'date_planned': fields.Datetime.now(),
            'product_qty': 10,
            'product_uom': self.env.ref('product.product_uom_unit').id,
            'price_unit': 15,
        })
        self.assertEquals(po.amount_total, 150)

        # Create a line with price_unit_base
        line = po.order_line.create({
            'order_id': po.id,
            'product_id': product.id,
            'name': product.name,
            'date_planned': fields.Datetime.now(),
            'product_qty': 10,
            'product_uom': self.env.ref('product.product_uom_unit').id,
            'price_unit_base': 15,
        })
        self.assertEquals(po.amount_total, 300)

        # Change the price_unit of my line
        line.price_unit = 10
        self.assertEquals(po.amount_total, 250)
        self.assertEquals(line.price_unit, 10)
        self.assertEquals(line.price_unit_base, 10)

        # Add a discount of 50% on the last line
        line.discount_global = 50
        self.assertEquals(po.amount_total, 200)

        # Add a pricelist discount of 10%
        # (this discount will be add to the discount of 50%)
        line.discount_pricelist = 10
        self.assertEquals(po.amount_total, 195)
