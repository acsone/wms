# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from contextlib import contextmanager

from odoo.tests.common import SavepointCase


class TestInstancePickingState(SavepointCase):

    @contextmanager
    def mock_with_delay(self):
        with mock.patch('odoo.addons.queue_job.models.base.DelayableRecordset',
                        name='DelayableRecordset', spec=True
                        ) as delayable_cls:
            # prepare the mocks
            delayable = mock.MagicMock(name='DelayableBinding')
            delayable_cls.return_value = delayable
            yield delayable_cls, delayable

    @classmethod
    def setUpClass(cls):
        super(TestInstancePickingState, cls).setUpClass()
        # TODO make a common class
        cls.partner1 = cls.env['res.partner'].create({
            'name': 'Unittest partner',
            'ref': '12344566777878',
        })
        cls.partner2 = cls.env['res.partner'].create({
            'name': 'Unittest partner',
            'ref': '12344566777879',
        })
        cls.partner3 = cls.env['res.partner'].create({
            'name': 'Unittest partner',
            'ref': '12344566777874',
        })
        cls.p1 = cls.env['product.product'].create({
            'name': 'Unittest P1',
            'uom_id': cls.env.ref('product.product_uom_unit').id,
            'type': 'product',
        })
        cls.p2 = cls.env['product.product'].create({
            'name': 'Unittest P2',
            'uom_id': cls.env.ref('product.product_uom_unit').id,
            'type': 'product',
        })

        cls.delivery_template = cls.env['round.template'].create({
            'name': 'Unittest delivery template',
        })

        cls.delivery_round_1 = cls.env['round.instance'].create({
            'template_id': cls.delivery_template.id,
            'date': '2017-01-01',
        })

        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'Base Warehouse',
            'reception_steps': 'one_step',
            'delivery_steps': 'pick_ship',
            'code': 'BWH'})

        inventory = cls.env['stock.inventory'].create({
            'name': 'Test',
            'product_id': cls.p1.id,
            'filter': 'product'})
        inventory.prepare_inventory()
        assert not inventory.line_ids, "Inventory line should not created."
        cls.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': cls.p1.id,
            'product_uom_id': cls.env.ref('product.product_uom_unit').id,
            'product_qty': 100,
            'location_id': cls.env.ref('stock.stock_location_stock').id,
        })
        cls.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': cls.p1.id,
            'product_uom_id': cls.env.ref('product.product_uom_unit').id,
            'product_qty': 100,
            'location_id': cls.warehouse_1.wh_output_stock_loc_id.id,
        })
        inventory.action_done()

    def _create_picking_pick(self, partner=None):
        if not partner:
            partner = self.partner1
        warehouse = self.warehouse_1
        Picking = self.env['stock.picking']
        picking_values = {
            'partner_id': partner.id,
            'picking_type_id': warehouse.pick_type_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': warehouse.wh_output_stock_loc_id.id,
            'move_lines': [(0, 0, {
                'name': self.p1.name,
                'product_id': self.p1.id,
                'product_uom_qty': 1,
                'product_uom': self.p1.uom_id.id,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': warehouse.wh_output_stock_loc_id.id,
            })]
        }
        return Picking.create(picking_values)

    def _create_picking_out(self, partner=None):
        if not partner:
            partner = self.partner1
        warehouse = self.warehouse_1
        Picking = self.env['stock.picking']
        picking_values = {
            'partner_id': partner.id,
            'picking_type_id': warehouse.out_type_id.id,
            'location_id': warehouse.wh_output_stock_loc_id.id,
            'location_dest_id': self.env.ref(
                'stock.stock_location_customers'
            ).id,
            'move_lines': [(0, 0, {
                'name': self.p1.name,
                'product_id': self.p1.id,
                'product_uom_qty': 1,
                'product_uom': self.p1.uom_id.id,
                'location_id': warehouse.wh_output_stock_loc_id.id,
                'location_dest_id': self.env.ref(
                    'stock.stock_location_customers'
                ).id,
            })]
        }
        return Picking.create(picking_values)

    def test_picking_state_deliver_job(self):
        """Job that process a round.instance.picking.state"""
        ship1 = self._create_picking_out()
        self.env['stock.move'].create({
            'name': self.p1.name,
            'product_id': self.p1.id,
            'product_uom_qty': 1,
            'product_uom': self.p1.uom_id.id,
            'picking_id': ship1.id,
            'location_id': ship1.location_id.id,
            'location_dest_id': ship1.location_dest_id.id,
        })
        self.delivery_round_1._assign_pickings(ship1)
        self.assertEqual(ship1.state, 'assigned')
        icust = self.delivery_round_1.instance_customer_ids

        # for the test, we run it in the same transaction
        icust._deliver_job()
        self.assertEqual(icust.delivered, True)
        self.assertEqual(ship1.state, 'done')

    def test_round_fully_delivered(self):
        """Round goes from delivering to done"""
        self.assertEqual(self.delivery_round_1.state, 'pending')
        pick1 = self._create_picking_pick(partner=self.partner1)
        pick2 = self._create_picking_pick(partner=self.partner2)
        pick3 = self._create_picking_pick(partner=self.partner3)

        ship1 = self._create_picking_out(self.partner1)
        ship2 = self._create_picking_out(self.partner2)
        ship3 = self._create_picking_out(self.partner3)

        # we don't care about the details if it is really
        # in that state, it is only for the round to think it is
        pick1.move_lines.write({'state': 'assigned'})
        pick2.move_lines.write({'state': 'assigned'})
        pick3.move_lines.write({'state': 'waiting'})

        ship1.move_lines.write({'state': 'waiting'})
        ship2.move_lines.write({'state': 'waiting'})
        ship3.move_lines.write({'state': 'waiting'})

        pickings = pick1 | pick2 | pick3 | ship1 | ship2 | ship3
        self.delivery_round_1._assign_pickings(pickings)

        icusts = self.delivery_round_1.instance_customer_ids
        self.assertEqual(len(icusts), 2)
        # We did not manage move_dest_id so ship1/2 will be exluded
        self.assertEqual(set(icusts.mapped('picking_ids')), {pick1, pick2})

        pick1.move_lines.write({'state': 'done'})
        ship1.move_lines.write({'state': 'done'})

        with self.mock_with_delay() as (__, __):
            self.delivery_round_1.button_deliver()

        # for the test, we run it in the same transaction
        icusts[0]._deliver_job()
        self.delivery_round_1.recheck_delivery_state()
        self.assertEqual(self.delivery_round_1.state, 'delivering')

        icusts[1]._deliver_job()
        self.delivery_round_1.recheck_delivery_state()
        self.assertEqual(self.delivery_round_1.state, 'done')

        # pick2 is not done so should be removed from the round
        self.assertEqual(
            set(self.delivery_round_1.instance_customer_ids
                .mapped('picking_ids')),
            {pick1})
