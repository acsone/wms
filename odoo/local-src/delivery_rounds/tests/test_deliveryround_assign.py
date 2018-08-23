# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, at_install, post_install


class TestDeliveryRoundAssign(TransactionCase):

    def setUp(self):
        super(TestDeliveryRoundAssign, self).setUp()

        self.partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
            'ref': '12344566777878',
        })

        self.p1 = self.env['product.product'].create({
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'product',
        })
        self.p2 = self.env['product.product'].create({
            'name': 'Unittest P2',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'product',
        })

        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'product_id': self.p1.id,
            'filter': 'product'})
        inventory.prepare_inventory()
        self.assertFalse(inventory.line_ids,
                         "Inventory line should not created.")
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.p1.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'product_qty': 100,
            'location_id': self.env.ref('stock.stock_location_stock').id})
        inventory.action_done()

        self.delivery_template = self.env['round.template'].create({
            'name': 'Unittest delivery template',
        })

        self.delivery_round_1 = self.env['round.instance'].create({
            'template_id': self.delivery_template.id,
            'date': '2017-01-01',
        })

        # pick/ship
        pick = self.env['stock.picking.type'].search([('name', '=', 'Pick')])
        if not pick:
            pick = self.env['stock.picking.type'].search([
                ('name', '=', 'Delivery Orders')])
        pick.write({'subcode': 'PICK'})

    @post_install(True)
    @at_install(False)
    def test_deliveryround_carrier(self):
        delivery_template = self.env['round.template'].create({
            'name': 'Unittest delivery template',
        })
        delivery_carrier_fixed = self.env['delivery.carrier'].create({
            'name': 'Unittest shipping costs',
            'delivery_type': 'fixed',
            'fixed_price': 10.0,
            'delivery_template_id': delivery_template.id,
        })
        delivery_round = self.env['round.instance'].create({
            'name': 'Unittest delivery round',
            'template_id': delivery_template.id,
            'date': '2017-01-01',
        })
        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'carrier_id': delivery_carrier_fixed.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'price_unit': 200,
                }),
            ]
        })
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        for picking in sale.picking_ids:
            self.assertEqual(
                picking.delivery_round_id.id,
                delivery_round.id
            )

    @post_install(True)
    @at_install(False)
    def test_force_deliveryround_partially_available(self):
        self.assertEqual(self.p1.qty_available, 100)
        self.assertEqual(self.p2.qty_available, 0)

        sale = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.p1.name,
                    'product_id': self.p1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 3,
                    'price_unit': 200,
                }),
                (0, 0, {
                    'name': self.p2.name,
                    'product_id': self.p2.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 5,
                    'price_unit': 200,
                }),
            ]
        })
        self.assertFalse(sale.picking_ids)
        sale.action_confirm()

        # P1 available, P2 not available. Force delivery round on picking
        pick = sale.picking_ids.filtered(
            lambda p: p.picking_type_subcode == 'PICK')

        self.delivery_round_1._assign_pickings(pick)

        # One line is available, so assignment must succeed
        for picking in sale.picking_ids:
            self.assertEqual(
                picking.delivery_round_id.id,
                self.delivery_round_1.id
            )

        self.assertEqual(pick.state, 'partially_available')
        self.assertEqual(pick.pack_operation_ids.mapped('product_id'), self.p1)

        return sale

    @post_install(True)
    @at_install(False)
    def test_reassign_on_reception(self):
        sale = self.test_force_deliveryround_partially_available()
        pick = sale.picking_ids.filtered(
            lambda p: p.picking_type_subcode == 'PICK')

        # Make P2 available. Picking must automatically reserve P2
        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'product_id': self.p2.id,
            'filter': 'product'})
        inventory.prepare_inventory()
        self.assertFalse(inventory.line_ids,
                         "Inventory line should not created.")
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.p2.id,
            'product_uom_id': self.ref('product.product_uom_unit'),
            'product_qty': 200,
            'location_id': self.env.ref('stock.stock_location_stock').id})
        inventory.action_done()

        for picking in sale.picking_ids:
            self.assertEqual(
                picking.delivery_round_id.id,
                self.delivery_round_1.id
            )

        self.assertEqual(pick.state, 'assigned')
        self.assertEqual(set(pick.pack_operation_ids.mapped('product_id')),
                         set([self.p1, self.p2]))
