# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from freezegun import freeze_time
from odoo import fields
from odoo.tests.common import SavepointCase


class TestPurchaseOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()

        # workaround for active sale exceptions making tests fail
        if 'exception.rule' in cls.env:
            cls.env['exception.rule'].search([]).write({'active': False})

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.supplier = cls.env.ref('base.res_partner_12')
        cls.product = cls.env['product.product'].create({'name': 'Product 1'})
        cls.route_mto = cls.env.ref('stock.route_warehouse0_mto')
        cls.route_buy = cls.env.ref('purchase.route_warehouse0_buy')
        cls.route_mto_mts = cls.env.ref('stock_mts_mto_rule.route_mto_mts')
        cls.partner = cls.env.ref('base.res_partner_1')

        cls.so1 = cls.env['sale.order'].create(
            {
                'partner_id': cls.partner.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': cls.product.name,
                            'product_id': cls.product.id,
                            'product_uom': cls.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 365,
                            'price_unit': 50,
                        },
                    )
                ],
            }
        )

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
        bank_holiday.create({'name': '2 January', 'date': '2017-01-02'})
        bank_holiday.create({'name': '9 January', 'date': '2017-01-09'})

        pol = self.env['purchase.order.line']

        seller = self.env['product.supplierinfo'].create(
            {'name': self.supplier.id, 'min_qty': 0, 'price': 100, 'delay': 3}
        )

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

        po = self.env['purchase.order'].create(
            {
                'partner_id': self.supplier.id,
                'date_order': fields.Datetime.now(),
                'date_planned': fields.Datetime.now(),
            }
        )

        # Create a line with price_unit (old style)
        # Keep only for compatibility
        line1 = po.order_line.create(
            {
                'order_id': po.id,
                'product_id': self.product.id,
                'name': self.product.name,
                'date_planned': fields.Datetime.now(),
                'product_qty': 10,
                'product_uom': self.env.ref('product.product_uom_unit').id,
                'price_unit': 15,
            }
        )
        self.assertEqual(line1.price_unit, line1.price_unit_base)
        self.assertEqual(po.amount_total, 150)

        # Create a line with price_unit_base
        line2 = po.order_line.create(
            {
                'order_id': po.id,
                'product_id': self.product.id,
                'name': self.product.name,
                'date_planned': fields.Datetime.now(),
                'product_qty': 10,
                'product_uom': self.env.ref('product.product_uom_unit').id,
                'price_unit_base': 15,
            }
        )
        self.assertEqual(po.amount_total, 300)

        # Change the price_unit of my line
        line2.price_unit_base = 10
        line2._onchange_price_unit()
        self.assertEqual(line2.price_unit, 10)
        self.assertEqual(line2.price_unit_base, 10)
        self.assertEqual(po.amount_total, 250)

        # Add a discount of 50% on the last line
        line2.discount_global = 50
        line2._onchange_price_unit()
        self.assertEqual(po.amount_total, 200)

        # Add a pricelist discount of 10%
        # (this discount will be add to the discount of 50%)
        line2.promotion_supplier = 10
        line2._onchange_price_unit()
        self.assertEqual(po.amount_total, 195)

    def test_unit_price_onchange(self):
        """ Test unit price discount with cache object """
        line = self.env['purchase.order.line'].new(
            {'product_qty': 10, 'price_unit_base': 15}
        )
        # Change the base_price_unit of my line
        # (price_unit is not visible on view)
        line.price_unit_base = 10
        line._onchange_price_unit()
        self.assertEqual(line.price_total, 100)
        self.assertEqual(line.price_unit, 10)
        self.assertEqual(line.price_unit_base, 10)

        # Add a discount of 50% on the last line
        line.discount_global = 50
        line._onchange_price_unit()
        self.assertEqual(line.price_total, 50)

        # Add a pricelist discount of 10%
        # (this discount will be add to the discount of 50%)
        line.promotion_supplier = 10
        line._onchange_price_unit()
        self.assertEqual(line.price_total, 45)

    def test_promotion_supplier(self):

        supplierinfo = self.env['product.supplierinfo'].create(
            {'name': self.supplier.id, 'discount_purchase': 10}
        )

        purchase = self.env['purchase.order'].create(
            {
                'partner_id': self.supplier.id,
                'order_line': [
                    (
                        0,
                        False,
                        {
                            'name': self.product.name,
                            'date_planned': fields.Datetime.now(),
                            'product_id': self.product.id,
                            'product_qty': 1,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'price_unit_base': 100,
                        },
                    )
                ],
            }
        )

        line = purchase.order_line

        self.assertEqual(line.promotion_supplier, 0)
        self.assertEqual(line.price_unit_base, 100)
        self.assertEqual(line.price_unit, 100)
        self.assertEqual(purchase.amount_untaxed, 100)

        self.product.write({'seller_ids': [(6, 0, supplierinfo.ids)]})
        line._set_promotion_supplier()
        line._onchange_price_unit()

        self.assertEqual(line.promotion_supplier, 10)
        self.assertEqual(line.price_unit_base, 100)
        self.assertEqual(line.price_unit, 90)
        self.assertEqual(purchase.amount_untaxed, 90)

    def _create_procurement(self, **values):
        Procurement = self.env['procurement.order']
        procurement = Procurement.new(values)
        procurement.onchange_product_id()
        return Procurement.create(
            procurement._convert_to_write(procurement._cache)
        )

    def test_procurement_make_po(self):
        """Test a purchase created from procurement gets promotions
        computed"""

        warehouse = self.env.ref('stock.warehouse0')

        procurement = self._create_procurement(
            partner_id=self.supplier.id,
            rule_id=warehouse.buy_pull_id.id,
            product_id=self.product.id,
            name='Procurement Make PO',
            product_qty=1.0,
        )

        # price with taxes
        price = 100
        supplierinfo = self.env['product.supplierinfo'].create(
            {
                'name': self.supplier.id,
                'discount_purchase': 10,
                'price': price,
                'currency_id': self.env.ref('base.EUR').id,
            }
        )
        self.product.write(
            {
                'seller_ids': [(6, 0, supplierinfo.ids)],
                # deflect side effect of other modules adding
                # taxes by unlinking all taxes
                'supplier_taxes_id': [(5, False, False)],
            }
        )

        procurement.make_po()
        purchase = procurement.purchase_id

        line = purchase.order_line.filtered(
            lambda rec: rec.product_id == self.product
        )

        self.assertEqual(line.promotion_supplier, 10)
        self.assertEqual(line.price_unit_base, 100)
        self.assertEqual(line.price_unit, 90)
        self.assertEqual(purchase.amount_untaxed, 90)

    @freeze_time("2018-06-01", as_arg=True)
    def test_nb_days_out_of_stock_computation(frozen_time, self):
        # without the route_mto, route_mto_mts
        self.assertNotIn(self.route_mto.id, self.product.route_ids.ids)
        self.assertNotIn(self.route_mto_mts.id, self.product.route_ids.ids)
        # There should be only one variant
        self.assertEqual(self.product.product_variant_count, 1)
        # there are no SO in past so it will be null
        self.assertEqual(self.product.nb_days_out_of_stock, 0)

        frozen_time.move_to('2018-07-20 12:00:00')
        self.so1.action_confirm()
        # Ensure fields are computed after the sale order is confirmed
        frozen_time.move_to('2018-07-21 00:00:00')
        self.so1.refresh()
        self.product.refresh()

        self.env['stock.quant'].create(
            {
                'product_id': self.product.id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'qty': self.so1.order_line[0].product_qty,
            }
        )

        self.so1.refresh()
        self.product.refresh()

        # There is a SO in past and stock is used
        self.assertEqual(self.product.virtual_available, 0.0)
        self.assertEqual(self.product.nb_days_out_of_stock, 0)
        self.assertEqual(
            self.product.product_variant_id.average_annual_consumption,
            round(float(365) / 12, 2),
        )

        # we update stock
        self.env['stock.quant'].create(
            {
                'product_id': self.product.id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'qty': self.so1.order_line[0].product_qty,
            }
        )

        self.so1.refresh()
        self.product.refresh()

        self.assertNotIn(self.route_mto.id, self.product.route_ids.ids)
        self.assertNotIn(self.route_mto_mts.id, self.product.route_ids.ids)

        self.assertEqual(self.product.virtual_available, 365)
        self.assertEqual(
            self.product.product_variant_id.average_annual_consumption,
            round(float(365) / 12, 2),
        )
        self.assertEqual(self.product.nb_days_out_of_stock, 365)

    def test_nb_days_out_of_stock_route_mto(self):
        # With the route_mto
        self.product.write({'route_ids': [(4, self.route_mto.id, False)]})
        self.product.refresh()
        self.assertIn(self.route_mto.id, self.product.route_ids.ids)
        self.assertEqual(self.product.nb_days_out_of_stock, 0)

    def test_nb_days_out_of_stock_route_mto_mts(self):
        # With the route_mto_mts
        self.product.write({'route_ids': [(4, self.route_mto_mts.id, False)]})
        self.product.refresh()
        self.assertIn(self.route_mto_mts.id, self.product.route_ids.ids)
        self.assertEqual(self.product.nb_days_out_of_stock, 0)
