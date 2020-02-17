# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.addons.partner_schedule.tests.test_working_schedule import (
    TestCustomerWorkingScheduleBase,
)
from odoo.tests.common import SavepointCase

from .common import DeliveryRoundTestCase


class TestDeliveryRoundAssignMixin(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestDeliveryRoundAssignMixin, cls).setUpClass()

        cls.partner = cls.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '12344566777878'}
        )

        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'Unittest P1',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
            }
        )
        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'Unittest P2',
                'uom_id': cls.env.ref('product.product_uom_unit').id,
                'type': 'product',
            }
        )

        cls._add_inventory_qty(cls.p1, 100)

        cls.delivery_template = cls.env['round.template'].create(
            {'name': 'Unittest delivery template'}
        )

        cls.delivery_round_1 = cls.env['round.instance'].create(
            {'template_id': cls.delivery_template.id, 'date': '2017-01-01'}
        )
        cls.delivery_round_2 = cls.env['round.instance'].create(
            {'template_id': cls.delivery_template.id, 'date': '2017-01-01'}
        )

        # pick/ship
        pick = cls.env['stock.picking.type'].search([('name', '=', 'Pick')])
        if not pick:
            pick = cls.env['stock.picking.type'].search(
                [('name', '=', 'Delivery Orders')]
            )
        pick.write({'subcode': 'PICK'})

    @classmethod
    def _add_inventory_qty(cls, product, qty):
        inventory = cls.env['stock.inventory'].create(
            {'name': 'Test', 'product_id': product.id, 'filter': 'product'}
        )
        inventory.prepare_inventory()
        assert not inventory.line_ids, "Inventory line should not created."
        cls.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'product_qty': qty,
                'location_id': cls.env.ref('stock.stock_location_stock').id,
            }
        )
        inventory.action_done()
        return inventory

    @classmethod
    def _prepare_delivery_round(cls):
        delivery_template = cls.env['round.template'].create(
            {'name': 'Unittest delivery template'}
        )
        delivery_carrier_fixed = cls.env['delivery.carrier'].create(
            {
                'name': 'Unittest shipping costs',
                'delivery_type': 'fixed',
                'fixed_price': 10.0,
                'delivery_template_id': delivery_template.id,
            }
        )
        delivery_round = cls.env['round.instance'].create(
            {'template_id': delivery_template.id, 'date': '2017-01-01'}
        )
        return delivery_carrier_fixed, delivery_round


class TestDeliveryRoundAssign(TestDeliveryRoundAssignMixin):
    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super(TestDeliveryRoundAssign, cls).setUpClass()

    def test_deliveryround_carrier(self):
        delivery_carrier_fixed, delivery_round = self._prepare_delivery_round()
        sale = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
                'carrier_id': delivery_carrier_fixed.id,
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
                            'price_unit': 200,
                        },
                    )
                ],
            }
        )
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        for picking in sale.picking_ids:
            self.assertEqual(picking.delivery_round_id.id, delivery_round.id)
            self.assertEqual(picking.group_id.carrier_id, sale.carrier_id)

    def test_force_deliveryround_partially_available(self):
        self.assertEqual(self.p1.qty_available, 100)
        self.assertEqual(self.p2.qty_available, 0)

        sale = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
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
                    ),
                    (
                        0,
                        0,
                        {
                            'name': self.p2.name,
                            'product_id': self.p2.id,
                            'product_uom': self.ref(
                                'product.product_uom_unit'
                            ),
                            'product_uom_qty': 5,
                            'price_unit': 200,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        # P1 available, P2 not available. Force delivery round on picking
        pick = sale.picking_ids.filtered(
            lambda p: p.picking_type_subcode == 'PICK'
        )

        self.delivery_round_1._assign_pickings(pick)

        # One line is available, so assignment must succeed
        for picking in sale.picking_ids:
            self.assertEqual(
                picking.delivery_round_id.id, self.delivery_round_1.id
            )

        self.assertEqual(pick.state, 'partially_available')
        self.assertEqual(pick.pack_operation_ids.mapped('product_id'), self.p1)

        return sale

    def test_reassign_on_reception(self):
        sale = self.test_force_deliveryround_partially_available()
        # pick = sale.picking_ids.filtered(
        #     lambda p: p.picking_type_subcode == 'PICK')

        # Make P2 available. Picking must automatically reserve P2
        inventory = self.env['stock.inventory'].create(
            {'name': 'Test', 'product_id': self.p2.id, 'filter': 'product'}
        )
        inventory.prepare_inventory()
        self.assertFalse(
            inventory.line_ids, "Inventory line should not created."
        )
        self.env['stock.inventory.line'].create(
            {
                'inventory_id': inventory.id,
                'product_id': self.p2.id,
                'product_uom_id': self.ref('product.product_uom_unit'),
                'product_qty': 200,
                'location_id': self.env.ref('stock.stock_location_stock').id,
            }
        )
        inventory.action_done()

        for picking in sale.picking_ids:
            self.assertEqual(
                picking.delivery_round_id.id, self.delivery_round_1.id
            )

        # TODO Adapt the test
        # The reasign of the picking is done by an another module
        # We need to move this test to this new module.
        # self.assertEqual(pick.state, 'assigned')
        # self.assertEqual(set(pick.pack_operation_ids.mapped('product_id')),
        #                  set([self.p1, self.p2]))

    def test_manual_change_delivery_round(self):
        sale = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
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
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        pick = sale.picking_ids.filtered(
            lambda p: p.picking_type_subcode == 'PICK'
        )

        self.delivery_round_1._assign_pickings(pick)
        for picking in sale.picking_ids:
            self.assertEqual(
                picking.delivery_round_id.id, self.delivery_round_1.id
            )

        delivery_round_2 = self.env['round.instance'].create(
            {'template_id': self.delivery_template.id, 'date': '2017-01-01'}
        )
        ship = sale.picking_ids.filtered(
            lambda p: p.picking_type_id.code == 'outgoing'
        )
        self.env['picking.assign.delivery.round'].with_context(
            active_ids=ship.ids
        ).create({'delivery_round_id': delivery_round_2.id}).confirm()

        carrier_manual_change = self.env.ref(
            'delivery_rounds.delivery_carrier_manual_round_change'
        )
        for picking in sale.picking_ids:
            self.assertEqual(picking.delivery_round_id.id, delivery_round_2.id)
            self.assertEqual(
                picking.group_id.carrier_id, carrier_manual_change
            )

    def test_assign_delivery_round_already_printed(self):
        sale = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
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
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        pick = sale.picking_ids.filtered(
            lambda p: p.picking_type_subcode == 'PICK'
        )
        self.delivery_round_1._assign_pickings(pick)
        self.assertEqual(pick.state, 'assigned')
        self.assertTrue(pick.pack_operation_product_ids)
        self.assertFalse(pick.printed)

        # should be able to reassign as it is not yet printed
        self.delivery_round_2._assign_pickings(pick)
        for picking in sale.picking_ids:
            self.assertEqual(picking.delivery_round_id, self.delivery_round_2)
        # should not have changed
        self.assertEqual(pick.state, 'assigned')
        self.assertTrue(pick.pack_operation_product_ids)
        self.assertFalse(pick.printed)

        # from stock_picking_assignment: set an operator and printed to True
        pick.assign_operator()
        self.assertEqual(pick.state, 'assigned')
        self.assertTrue(pick.pack_operation_product_ids)
        self.assertTrue(pick.printed)

        # when a picking is started and has pack operations, we cannot
        # change it's delivery round
        expected_msg = 'You cannot reassign the started picking'
        with self.assertRaisesRegexp(exceptions.UserError, expected_msg):
            self.delivery_round_1._assign_pickings(pick)

    def test_assign_delivery_round_new_picking(self):
        """New picking on a SO can still be added to a delivery round"""
        sale = self.env['sale.order'].create(
            {
                'partner_id': self.partner.id,
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
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        pick = sale.picking_ids.filtered(
            lambda p: p.picking_type_subcode == 'PICK'
        )
        self.delivery_round_1._assign_pickings(pick)
        pick.assign_operator()
        self.assertEqual(pick.state, 'assigned')
        self.assertTrue(pick.pack_operation_product_ids)
        self.assertTrue(pick.printed)

        self._add_inventory_qty(self.p2, 100)

        self.env['sale.order.line'].create(
            {
                'order_id': sale.id,
                'name': self.p2.name,
                'product_id': self.p2.id,
                'product_uom': self.ref('product.product_uom_unit'),
                'product_uom_qty': 3,
                'price_unit': 200,
            }
        )
        new_pick = sale.picking_ids.filtered(lambda r: r.state == 'confirmed')
        self.assertEqual(len(new_pick), 1)

        # manually setting delivery round on the new picking
        # must be possible
        self.delivery_round_1._assign_pickings(new_pick)
        self.assertEqual(new_pick.delivery_round_id, self.delivery_round_1)


class TestRoundWithCustomerWorkingSchedule(
    TestCustomerWorkingScheduleBase,
    DeliveryRoundTestCase,
    TestDeliveryRoundAssignMixin,
):
    def test_assign_picking(self):
        ship1 = self._create_picking_out()
        self.create_schedule({'partner_id': self.partner1.id})
        self.env['stock.move'].create(
            {
                'name': self.p1.name,
                'product_id': self.p1.id,
                'product_uom_qty': 1,
                'product_uom': self.p1.uom_id.id,
                'picking_id': ship1.id,
                'location_id': ship1.location_id.id,
                'location_dest_id': ship1.location_dest_id.id,
            }
        )
        self.delivery_round_1.date = '2019-01-06'
        delivery_round = self.delivery_round_1.with_context(
            manual_change_delivery_round=True
        )
        with self.assertRaises(exceptions.UserError):
            # delivery can be done only on allowed date
            delivery_round._assign_pickings(ship1)

        delivery_round.date = '2019-02-01'
        delivery_round._assign_pickings(ship1)
        self.assertEqual(ship1.state, 'assigned')

    def test_deliveryround_carrier_schedule(self):
        delivery_carrier_fixed, delivery_round = self._prepare_delivery_round()
        self.create_schedule(
            {
                'partner_id': self.partner1.id,
                'start_date': '2017-01-01',
                'end_date': '2017-01-01',
            }
        )
        sale = self.env['sale.order'].create(
            {
                'partner_id': self.partner1.id,
                'carrier_id': delivery_carrier_fixed.id,
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
                            'price_unit': 200,
                        },
                    )
                ],
            }
        )
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        for picking in sale.picking_ids:
            self.assertFalse(picking.delivery_round_id.id)
