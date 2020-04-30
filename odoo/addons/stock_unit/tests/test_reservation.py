# -*- coding: utf-8 -*-


from odoo.tests.common import TransactionCase


class TestReservationUnit(TransactionCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestReservationUnit, self).setUp()

        self.product_1 = self.env['product.product'].create(
            {
                'name': 'Product 1',
                'type': 'product',
                'uom_id': self.env.ref('product.product_uom_unit').id,
                'uom_po_id': self.env.ref('product.product_uom_unit').id,
                'default_code': 'Code product 1',
                'unit_in_pallet': 80,
                'unit_in_box': 20,
                'unit_in_shrink_wrap': 8,
            }
        )

    def test_unit(self):
        location = self.env['stock.location'].create({'name': 'Test Unit'})
        # Put 1 product in stock
        inventory = self.env['stock.inventory'].create(
            {
                'name': 'Test unit',
                'filter': 'product',
                'location_id': location.id,
                'product_id': self.product_1.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.unlink()
        inventory.line_ids.create(
            {
                'product_id': self.product_1.id,
                'product_qty': 1.0,
                'inventory_id': inventory.id,
                'location_id': location.id,
            }
        )
        inventory.action_done()
        # Put 1 box in stock
        inventory = self.env['stock.inventory'].create(
            {
                'name': 'Test unit',
                'filter': 'product',
                'location_id': location.id,
                'product_id': self.product_1.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.write(
            {
                'product_id': self.product_1.id,
                'product_qty': 21.0,
                'inventory_id': inventory.id,
                'location_id': location.id,
            }
        )
        inventory.action_done()
        # Put 1 pallet in stock
        inventory = self.env['stock.inventory'].create(
            {
                'name': 'Test unit',
                'filter': 'product',
                'location_id': location.id,
                'product_id': self.product_1.id,
            }
        )
        inventory.prepare_inventory()
        inventory.line_ids.write(
            {
                'product_id': self.product_1.id,
                'product_qty': 101.0,
                'inventory_id': inventory.id,
                'location_id': location.id,
            }
        )
        inventory.action_done()

        quants = self.env['stock.quant'].search(
            [('location_id', '=', location.id)]
        )
        # There should be 3 quants in stock
        self.assertEqual(len(quants), 3)
        self.assertTrue(
            quants.mapped('qty') == [1.0, 20.0, 80.0],
            'Unexpected quants qty in stock',
        )

        # Create test move
        loc_customer = self.env.ref('stock.stock_location_customers')
        picking = self.env['stock.picking'].create(
            {
                'picking_type_id': self.env.ref('stock.picking_type_out').id,
                'location_id': location.id,
                'location_dest_id': loc_customer.id,
            }
        )
        move = self.env['stock.move'].create(
            {
                'picking_id': picking.id,
                'name': 'Test unit',
                'product_id': self.product_1.id,
                'product_uom': self.product_1.uom_id.id,
                'product_uom_qty': 20,
                'location_id': location.id,
                'location_dest_id': loc_customer.id,
            }
        )
        picking.with_context(round_autoset=False).action_assign()
        quant = move.reserved_quant_ids
        # 1 quant should have been reserved
        self.assertEqual(len(quant), 1)
        # quant reserved quantity should be 20
        self.assertEqual(quant.qty, 20)
