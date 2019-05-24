# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestDeliveryRoundAssign(SavepointCase):
    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super(TestDeliveryRoundAssign, cls).setUpClass()

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

        inventory = cls.env['stock.inventory'].create(
            {'name': 'Test', 'product_id': cls.p1.id, 'filter': 'product'}
        )
        inventory.prepare_inventory()
        assert not inventory.line_ids, "Inventory line should not created."
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

        cls.delivery_template = cls.env['round.template'].create(
            {'name': 'Unittest delivery template'}
        )

        cls.delivery_round_1 = cls.env['round.instance'].create(
            {'template_id': cls.delivery_template.id, 'date': '2017-01-01'}
        )

        # pick/ship
        pick = cls.env['stock.picking.type'].search([('name', '=', 'Pick')])
        if not pick:
            pick = cls.env['stock.picking.type'].search(
                [('name', '=', 'Delivery Orders')]
            )
        pick.write({'subcode': 'PICK'})

    def test_deliveryround_carrier(self):
        delivery_template = self.env['round.template'].create(
            {'name': 'Unittest delivery template'}
        )
        delivery_carrier_fixed = self.env['delivery.carrier'].create(
            {
                'name': 'Unittest shipping costs',
                'delivery_type': 'fixed',
                'fixed_price': 10.0,
                'delivery_template_id': delivery_template.id,
            }
        )
        delivery_round = self.env['round.instance'].create(
            {
                'name': 'Unittest delivery round',
                'template_id': delivery_template.id,
                'date': '2017-01-01',
            }
        )
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
