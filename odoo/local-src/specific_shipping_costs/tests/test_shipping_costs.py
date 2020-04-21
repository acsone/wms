# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestShippingCosts(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestShippingCosts, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create the product used for "shipping alcyon fees" and is xmlid
        cls.product_shipping_cost = cls.env['product.product'].create(
            {'name': 'Alcyon shipping cost test'}
        )
        # Create the delivery carrier for Alcyon
        cls.fee = 8.5
        cls.delivery_method = cls.env['delivery.carrier'].create(
            {
                'delivery_type': 'fixed',
                'fixed_price': cls.fee,
                'free_if_more_than': True,
                'amount': 125,
                'use_specific_cost_calculation': True,
                'name': 'Alcyon',
            }
        )
        cls.fee_2 = 20
        cls.delivery_method_2 = cls.env['delivery.carrier'].create(
            {
                'delivery_type': 'fixed',
                'fixed_price': cls.fee_2,
                'free_if_more_than': True,
                'amount': 200,
                'use_specific_cost_calculation': True,
                'name': 'Alcyon 2',
            }
        )

        cls.fee_3 = 25
        cls.delivery_method_3 = cls.env['delivery.carrier'].create(
            {
                'delivery_type': 'fixed',
                'fixed_price': cls.fee_3,
                'free_if_more_than': True,
                'amount': 200,
                'use_specific_cost_calculation': False,
                'name': 'Alcyon 3',
            }
        )
        # Lets create 2 customers
        cls.partner1 = cls.env['res.partner'].create(
            {
                'name': 'Partner One',
                'ref': '89328492342',
                'help_with_fee': True,
            }
        )
        cls.partner2 = cls.env['res.partner'].create(
            {
                'name': 'Partner Two',
                'ref': '498298349283',
                'help_with_fee': True,
            }
        )
        # Create a couple of products
        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'Unittest P1',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'consu',
            }
        )
        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'Unittest P2',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
            }
        )
        cls.p3 = cls.env['product.product'].create(
            {
                'name': 'Unittest P3',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
            }
        )
        # Add some stock for p1 and p2
        inventory = cls.env['stock.inventory'].create(
            {
                'name': 'Test',
                'location_id': cls.env.ref('stock.stock_location_stock').id,
                'filter': 'partial',
            }
        )
        inventory.prepare_inventory()
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': cls.p1.id,
                'product_uom_id': cls.env.ref('product.product_uom_unit').id,
                'product_qty': 100,
                'location_id': cls.env.ref('stock.stock_location_stock').id,
            }
        )
        inventory.action_done()
        inventory = cls.env['stock.inventory'].create(
            {
                'name': 'Test',
                'location_id': cls.env.ref('stock.stock_location_stock').id,
                'filter': 'partial',
            }
        )
        inventory.prepare_inventory()
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': cls.p2.id,
                'product_uom_id': cls.env.ref('product.product_uom_unit').id,
                'product_qty': 100,
                'location_id': cls.env.ref('stock.stock_location_stock').id,
            }
        )
        inventory.action_done()
        # Create a sale order 1 for partner 1
        cls.so1 = cls.env['sale.order'].create(
            {
                'partner_id': cls.partner1.id,
                'carrier_id': cls.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': cls.p1.name,
                            'product_id': cls.p1.id,
                            'product_uom': cls.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 1,
                            'price_unit': 50,
                        },
                    )
                ],
            }
        )
        # Create sale order 2 for partner 1
        cls.so2 = cls.env['sale.order'].create(
            {
                'partner_id': cls.partner1.id,
                'carrier_id': cls.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': cls.p1.name,
                            'product_id': cls.p1.id,
                            'product_uom': cls.env.ref(
                                'product.product_uom_unit'
                            ).id,
                            'product_uom_qty': 1,
                            'price_unit': 10,
                        },
                    )
                ],
            }
        )
        # Finally create 2 delivery round
        cls.delivery_template1 = cls.env['round.template'].create(
            {'name': 'Unittest delivery template'}
        )
        cls.dr1 = cls.env['round.instance'].create(
            {'template_id': cls.delivery_template1.id}
        )
        cls.delivery_template2 = cls.env['round.template'].create(
            {'name': 'Unittest delivery template'}
        )
        cls.dr2 = cls.env['round.instance'].create(
            {'template_id': cls.delivery_template2.id}
        )

    def get_shipping_cost(self, so):
        """Returns the amount of shipping cost billed on a sale order"""
        delivery_line = so.order_line.filtered('is_delivery')
        return sum(delivery_line.mapped('price_unit'))

    def product_used_for_cost_so_line(self, so):
        """Returns the product id used on the sale order line with thefee."""
        delivery_line = so.order_line.filtered('is_delivery')
        return delivery_line.product_id

    def no_shipping_line_present(self, so):
        delivery_line = so.order_line.filtered('is_delivery')
        return not bool(len(delivery_line))

    def test_customer_never_pay_fees(self):
        """Test a customer that should never pay shipping fees"""
        self.partner1.help_with_fee = False
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))

    def test_2_so_all_delivered_small_amount(self):
        """2 sale order for a small amount all delivered add fee"""
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertEqual(
            self.product_used_for_cost_so_line(self.so2),
            self.so2.carrier_id.product_id,
        )

    def test_2_so_all_delivered_large_amount(self):
        """2 sale order completely delivered large amount no fee"""
        self.so2.order_line[0].price_unit = 10
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))

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
        self.so2.write(
            {
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p3.name,
                            'product_id': self.p3.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 24,
                        },
                    )
                ]
            }
        )
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 20 % sale order 2
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        pick = self.so2.picking_ids
        self.dr1._assign_pickings(pick)
        op = pick.pack_operation_product_ids
        op = op.filtered(lambda r: r.product_id.id == self.p1.id)
        op.write({'qty_done': 1})
        pick.with_context(test_mode=True).do_transfer()
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        pick = self.so2.picking_ids.filtered(lambda r: r.state != 'done')
        self.dr2._assign_pickings(pick)
        pick.force_assign()
        op = pick.pack_operation_product_ids
        op.write({'qty_done': 1})

        pick.with_context(test_mode=True).do_transfer()
        self.dr2._deliver(background=False)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertEqual(self.get_shipping_cost(so3), self.fee)
        self.assertEqual(
            self.product_used_for_cost_so_line(so3), so3.carrier_id.product_id
        )

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
        self.so2.write(
            {
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p3.name,
                            'product_id': self.p3.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 24,
                        },
                    )
                ]
            }
        )
        self.so2.action_confirm()
        # First delivery : 100 % sale order 1 + 20 % sale order 2
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        pick = self.so2.picking_ids
        self.dr1._assign_pickings(pick)
        op = pick.pack_operation_product_ids
        op = op.filtered(lambda r: r.product_id.id == self.p1.id)
        op.write({'qty_done': 1})
        pick.with_context(test_mode=True).do_transfer()
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertTrue(self.no_shipping_line_present(self.so2))

        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        pick = self.so2.picking_ids.filtered(lambda r: r.state != 'done')
        self.dr2._assign_pickings(pick)
        pick.force_assign()
        op = pick.pack_operation_product_ids
        op.write({'qty_done': 1})

        pick.with_context(test_mode=True).do_transfer()
        self.dr2._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so2))
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
        self.dr1._deliver(background=False)
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertTrue(self.no_shipping_line_present(self.so2))

        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        self.dr2._assign_pickings(self.so2.picking_ids)
        self.dr2._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so2))
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
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertTrue(self.no_shipping_line_present(self.so2))
        # Second delivery round
        # Create a 3rd sale order
        so3 = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 70,
                        },
                    )
                ],
            }
        )
        so3.action_confirm()
        self.dr2._assign_pickings(so3.picking_ids)
        self.dr2._assign_pickings(self.so2.picking_ids)
        self.dr2._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so2))
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
        self.dr1._deliver(background=False)
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertTrue(self.no_shipping_line_present(self.so2))

        # Second delivery round
        self.dr2._assign_pickings(self.so2.picking_ids)
        self.dr2._deliver(background=False)
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertTrue(self.no_shipping_line_present(self.so2))

    def test_no_shipping_fees(self):
        """Small order in round but second so with large amount"""
        # Create a second sale order for partner One
        self.so2 = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 3,
                            'price_unit': 200,
                        },
                    )
                ],
            }
        )
        self.so1.action_confirm()
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))

    def test_multiple_customer_in_round(self):
        """2 customer in round, only partner 1 get charged """
        self.so1.action_confirm()
        self.so2.action_confirm()
        so21 = self.env['sale.order'].create(
            {
                'partner_id': self.partner2.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 1000,
                        },
                    )
                ],
            }
        )
        so21.action_confirm()
        self.dr1._assign_pickings(so21.picking_ids)
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._assign_pickings(self.so1.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so1))
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee)
        self.assertTrue(self.no_shipping_line_present(so21))

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
        self.dr1._deliver(background=False)
        self.assertEqual(self.get_shipping_cost(self.so1), self.fee)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee_2)

    def test_no_shipping_fees_no_specific_calc(self):
        """Order shouldn't have a fee and return in _add_delivery_cost_to_so"""
        # Create a second sale order for partner One
        self.so2 = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': self.delivery_method_3.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 5,
                            'price_unit': 200,
                        },
                    )
                ],
            }
        )
        self.so2.action_confirm()
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(self.so2))

    def test_shipping_fees_no_specific_calc(self):
        """Order should have a fee and pass through _add_delivery_cost_to_so"""
        # Create a second sale order for partner One
        self.so2 = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': self.delivery_method_3.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 10,
                        },
                    )
                ],
            }
        )
        self.so2.action_confirm()
        self.dr1._assign_pickings(self.so2.picking_ids)
        self.dr1._deliver(background=False)
        self.assertEqual(self.get_shipping_cost(self.so2), self.fee_3)

    def test_avoid_shiping_cost(self):
        """ If the outgoing picking type has avoid_shipping_cost at True
        there should be no fee. Test with use_specific_cost_calculation
        and without."""
        new_order = self.env['sale.order'].create(
            {
                'partner_id': self.partner2.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 10,
                        },
                    )
                ],
            }
        )
        new_order.action_confirm()
        self.dr1._assign_pickings(new_order.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.get_shipping_cost(new_order), self.fee)
        # Test with the same SO but we change the picking_type
        new_order = self.env['sale.order'].create(
            {
                'partner_id': self.partner2.id,
                'carrier_id': self.delivery_method.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 10,
                        },
                    )
                ],
            }
        )
        new_order.action_confirm()
        picking_type = new_order.picking_ids.filtered(
            lambda rec: rec.picking_type_code == 'outgoing').mapped(
            'picking_type_id')
        picking_type.avoid_shipping_cost = True
        self.dr1._assign_pickings(new_order.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(new_order))
        # Test with the delivery method 3 (With
        # use_specific_cost_calculation set to False)
        new_order = self.env['sale.order'].create(
            {
                'partner_id': self.partner2.id,
                'carrier_id': self.delivery_method_3.id,
                'order_line': [
                    (
                        0,
                        0,
                        {
                            'name': self.p1.name,
                            'product_id': self.p1.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 1,
                            'price_unit': 10,
                        },
                    )
                ],
            }
        )
        new_order.action_confirm()
        self.dr1._assign_pickings(new_order.picking_ids)
        self.dr1._deliver(background=False)
        self.assertTrue(self.no_shipping_line_present(new_order))
