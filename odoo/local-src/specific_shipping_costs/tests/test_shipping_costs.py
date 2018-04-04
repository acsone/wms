# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestShippingCosts(TransactionCase):

    def setUp(self):
        super(TestShippingCosts, self).setUp()

        # Create the product used for "shipping alcyon fees" and is xmlid
        self.product_shipping_cost = self.env['product.product'].create({
            'name': 'Alcyon shipping cost test'
        })
        # Create the delivery carrier for Alcyon
        self.fee = 8.5
        self.delivery_method = self.env['delivery.carrier'].create({
            'delivery_type': 'fixed',
            'fixed_price': self.fee,
            'free_if_more_than': True,
            'amount': 125,
            'use_specific_cost_calculation': True,
            'name': 'Alcyon',
        })
        self.fee_2 = 20
        self.delivery_method_2 = self.env['delivery.carrier'].create({
            'delivery_type': 'fixed',
            'fixed_price': self.fee_2,
            'free_if_more_than': True,
            'amount': 200,
            'use_specific_cost_calculation': True,
            'name': 'Alcyon 2',
        })

        self.env['ir.model.data'].create({
            'name': 'deliver_carrier_alcyon',
            'module': '__setup__',
            'model': 'delivery.carrier',
            'res_id': self.delivery_method.id,
        })
        self.env['ir.model.data'].create({
            'name': 'deliver_carrier_alcyon_product_product',
            'module': '__setup__',
            'model': 'product.product',
            'res_id': self.product_shipping_cost.id,
        })
        # Lets create 2 customers
        self.partner1 = self.env['res.partner'].create({
            'name': 'Partner One',
            'help_with_fee': True,
        })
        self.partner2 = self.env['res.partner'].create({
            'name': 'Partner Two',
            'help_with_fee': True,
        })
        # Create a couple of products
        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'consu',
        })
        self.p2 = self.env['product.product'].create({
            'name': 'Unittest P2',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'product',
        })
        self.p3 = self.env['product.product'].create({
            'name': 'Unittest P3',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'product',
        })
        # Add some stock for p1 and p2
        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.p1.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'product_qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id
            })
        inventory.action_done()
        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'filter': 'partial'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.p2.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'product_qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id
            })
        inventory.action_done()
        # Create a sale order 1 for partner 1
        self.so1 = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 50,
                }),
            ]
        })
        # Create sale order 2 for partner 1
        self.so2 = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 10,
                }),
            ]
        })
        # Finally create 2 delivery round
        self.dr1 = self.env['round.instance'].create({
            'name': 'Unittest delivery round',
        })
        self.dr2 = self.env['round.instance'].create({
            'name': 'Unittest delivery round 2',
        })

    def get_shipping_cost(self, so):
        """Returns the amount of shipping cost billed on a sale order"""
        delivery_line = so.order_line.filtered('is_delivery')
        return sum(delivery_line.mapped('price_unit'))

    def test_customer_never_pay_fees(self):
        """Test a customer that should never pay shipping fees"""
        self.partner1.help_with_fee = False
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)

    def test_2_so_all_delivered_small_amount(self):
        """2 sale order for a small amount all delivered add fee"""
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)

    def test_2_so_all_delivered_large_amount(self):
        """2 sale order completely delivered large amount no fee"""
        self.so2.order_line[0].price_unit = 10
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)

    def test_3_so_in_2_delivery_fee_twice(self):
        """Two deliveries both with fee

        The customer makes so1 (50 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 20% of so2 -> fees
        The customer makes so3 (70 EUR)
        Delivery 2: 80% so2 and so3 -> fees

        """
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.so2.order_line[0].price_unit = 6
        self.so2.write({'order_line': [
            (0, 0, {
                'name': self.p3.name,
                'product_id': self.p3.id,
                'product_uom': self.ref('product.product_uom_unit'),
                'product_uom_qty': 1,
                'price_unit': 24,
            }),
        ]})
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 20 % sale order 2
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        pick = self.so2.picking_ids
        self.dr1._assign_pickings(pick)
        op = pick.pack_operation_product_ids
        op = op.filtered(lambda r: r.product_id.id == self.p1.id)
        op.write({'qty_done': 1})
        result = pick.with_context(test_mode=True).do_new_transfer()
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 70,
                }),
            ]
        })
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        pick = self.so2.picking_ids.filtered(lambda r: r.state != 'done')
        self.dr2._assign_pickings(pick)
        pick.force_assign()
        op = pick.pack_operation_product_ids
        op.write({'qty_done': 1})

        result = pick.with_context(test_mode=True).do_new_transfer()
        self.assertEqual(result, None)
        self.dr2.button_confirm()
        self.dr2.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_3_so_in_2_delivery_fee_once(self):
        """Two deliveries one without fees the other one with it

        The customer makes so1 (100 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 20% of so2 -> no fees
        The customer makes so3 (70 EUR)
        Delivery 2: 80% so2 and so3 -> fees

        """
        self.so1.order_line[0].price_unit = 100
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.so2.order_line[0].price_unit = 6
        self.so2.write({'order_line': [
            (0, 0, {
                'name': self.p3.name,
                'product_id': self.p3.id,
                'product_uom': self.ref('product.product_uom_unit'),
                'product_uom_qty': 1,
                'price_unit': 24,
            }),
        ]})
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 20 % sale order 2
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        pick = self.so2.picking_ids
        self.dr1._assign_pickings(pick)
        op = pick.pack_operation_product_ids
        op = op.filtered(lambda r: r.product_id.id == self.p1.id)
        op.write({'qty_done': 1})
        result = pick.with_context(test_mode=True).do_new_transfer()
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)
        self.assertEqual(self.get_shipping_cost(self.so2), 0)
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 70,
                }),
            ]
        })
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        pick = self.so2.picking_ids.filtered(lambda r: r.state != 'done')
        self.dr2._assign_pickings(pick)
        pick.force_assign()
        op = pick.pack_operation_product_ids
        op.write({'qty_done': 1})

        result = pick.with_context(test_mode=True).do_new_transfer()
        self.assertEqual(result, None)
        self.dr2.button_confirm()
        self.dr2.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so2), 0)
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_3_so_in_2_delivery_fee_twice_2(self):
        """Two deliveries both with fee.

        The customer makes so1 (100 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 20% of so2 -> no fees
        The customer makes so3 (70 EUR)
        Delivery 2: 80% so2 and so3 -> fees

        """
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.so2.order_line[0].price_unit = 30
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 0 % sale order 2
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertEqual(self.get_shipping_cost(self.so2), 0)
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 70,
                }),
            ]
        })
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        self.dr2._assign_pickings(self.so2.picking_ids)
        self.dr2.button_confirm()
        self.dr2.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so2), 0)
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_3_so_in_2_delivery_fee_once_2(self):
        """Two deliveries one without fees the other one with it

        The customer makes so1 (100 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 0% of so2 -> no fees
        The customer makes so3 (70 EUR)
        Delivery 2: so2 and so3 -> fees

        """
        self.so1.order_line[0].price_unit = 100
        self.so1.action_confirm()
        self.so2.order_line[0].price_unit = 30
        self.so2.action_confirm()
        # First delivery
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)
        self.assertEqual(self.get_shipping_cost(self.so2), 0)
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 70,
                }),
            ]
        })
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        self.dr2._assign_pickings(self.so2.picking_ids)
        self.dr2.button_confirm()
        self.dr2.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so2), 0)
        self.assertEqual(self.get_shipping_cost(so3), self.fee)

    def test_no_so_between_delivery_no_fee(self):
        """Two deliveries one with fees the other one without

        The customer makes so1 (50 EUR) and so2 (30 EUR)
        Delivery 1: so1 and 0% of so2 -> fee
        Delivery 2: so2 -> no fees

        """
        self.so1.action_confirm()
        self.so2.order_line[0].price_unit = 30
        self.so2.action_confirm()
        # First delivery
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertEqual(self.get_shipping_cost(self.so2), 0)
        # Second delivery round
        self.dr2._assign_pickings(self.so2.picking_ids)
        self.dr2.button_confirm()
        self.dr2.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertEqual(self.get_shipping_cost(self.so2), 0)

    def test_no_shipping_fees(self):
        """Small order in round but second so with large amount"""
        # Create a second sale order for partner One
        self.so2 = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 3,
                    'price_unit': 200,
                }),
            ]
        })
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)

    def test_multiple_customer_in_round(self):
        """2 customer in round, only partner 1 get charged """
        self.so1.action_confirm()
        self.so2.action_confirm()
        so21 = self.env['sale.order'].create({
            'partner_id': self.partner2.id,
            'carrier_id': self.delivery_method.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 1000,
                }),
            ]
        })
        so21.action_confirm()
        self.dr1._assign_pickings(so21.picking_ids)
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), 0)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertEqual(self.get_shipping_cost(so21), 0)

    def test_one_customer_two_delivery_carrier(self):
        """1 customer 2 sale orders with 2 delivery carrier.

        He get charged twice.
        """
        self.so1.action_confirm()
        self.so2.carrier_id = self.delivery_method_2
        self.so2.order_line[0].price_unit = 170
        self.so2.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1.button_confirm()
        self.dr1.button_deliver()
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee_2)
