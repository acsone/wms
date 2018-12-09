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
        }
        return Picking.create(picking_values)

    def test_create_picking_state(self):
        """Deliver buttons generate round.instance.picking.state"""
        pick1 = self._create_picking_pick()
        pick2 = self._create_picking_pick()
        ship1 = self._create_picking_out()
        ship2 = self._create_picking_out()
        ship3 = self._create_picking_out()
        pickings = pick1 | pick2 | ship1 | ship2 | ship3
        self.delivery_round_1._assign_pickings(pickings)
        for p in pickings:
            self.assertEqual(p.state, 'assigned')

        # this one should not generate a picking state
        ship3.state = 'waiting'

        # we mock with_delay to ensure that jobs are created for the delivery
        # method
        with self.mock_with_delay() as (delayable_cls, delayable):
            self.delivery_round_1.button_deliver()
            picking_states = self.delivery_round_1.mapped(
                'instance_customer_ids.picking_state_ids'
            )
            self.assertEqual(len(picking_states), 2)
            self.assertEqual(
                set(picking_states.mapped('picking_id').ids),
                {ship1.id, ship2.id}
            )
            # with_delay has been called 2 times
            self.assertEqual(delayable_cls.call_count, 2)
            # the deliver method has been called 2 times on with_delay
            self.assertEqual(delayable.deliver.call_count, 2)

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
        pstate = self.env['round.instance.picking.state'].create({
            'picking_id': ship1.id,
            'instance_customer_id': icust.id,
        })

        # for the test, we run it in the same transaction
        pstate.deliver(new_cr=False)
        self.assertEqual(pstate.state, 'done')
        self.assertEqual(pstate.picking_id.state, 'done')

    def test_round_fully_delivered(self):
        """Round goes from delivering to done"""
        self.assertEqual(self.delivery_round_1.state, 'pending')
        pick1 = self._create_picking_pick()
        pick2 = self._create_picking_pick()
        ship1 = self._create_picking_out()
        ship2 = self._create_picking_out()
        ship3 = self._create_picking_out()
        pickings = pick1 | pick2 | ship1 | ship2 | ship3
        self.delivery_round_1._assign_pickings(pickings)
        for p in pickings:
            self.assertEqual(p.state, 'assigned')

        # let's say this one is waiting, should not be added to
        # the picking.state and then removed later from the round
        ship3.state = 'waiting'

        with self.mock_with_delay() as (__, __):
            self.delivery_round_1.button_deliver()

        pstates = self.delivery_round_1.mapped(
            'instance_customer_ids.picking_state_ids'
        )

        # we don't care about the details if it is really
        # done, it is only for the round to think it is done
        pick1.state = 'done'
        pick2.state = 'assigned'
        ship1.state = 'done'
        ship2.state = 'done'

        # for the test, we run it in the same transaction
        pstates[0].deliver(new_cr=False)
        self.delivery_round_1.recheck_delivery_state()
        self.assertEqual(self.delivery_round_1.state, 'delivering')

        pstates[1].deliver(new_cr=False)
        self.delivery_round_1.recheck_delivery_state()
        self.assertEqual(self.delivery_round_1.state, 'done')

        # pick2 and ship3 are not done so should be removed from the round
        self.assertEqual(
            set(self.delivery_round_1.mapped(
                'instance_customer_ids.picking_ids'
            ).ids),
            {pick1.id, ship1.id, ship2.id}
        )

    def test_delivered_compute_search(self):
        ship1 = self._create_picking_out()
        partner2 = self.env['res.partner'].create({
            'name': 'Unittest partner 2',
            'ref': '12344566777878',
        })
        ship2 = self._create_picking_out(partner=partner2)
        partner3 = self.env['res.partner'].create({
            'name': 'Unittest partner 3',
            'ref': '12344566777878',
        })
        ship3 = self._create_picking_out(partner=partner3)
        pickings = ship1 | ship2 | ship3
        self.delivery_round_1._assign_pickings(pickings)

        self.assertEqual(self.delivery_round_1.state, 'pending')
        icust = self.delivery_round_1.instance_customer_ids
        self.assertEqual(len(icust), 3)

        self.assertTrue(all(not i.delivered for i in icust))
        self.assertEquals(
            set(
                self.env['round.instance.customer'].search(
                    [
                        ('delivery_round_id', '=', self.delivery_round_1.id),
                        ('delivered', '=', True),
                    ]
                ).ids
            ),
            set([]),
        )

        with self.mock_with_delay() as (__, __):
            self.delivery_round_1.button_deliver()

        self.assertTrue(all(not i.delivered for i in icust))

        pstates = self.delivery_round_1.mapped(
            'instance_customer_ids.picking_state_ids'
        )
        pstate0, pstate1, pstate2 = pstates

        pstate0.deliver(new_cr=False)
        self.assertTrue(pstate0.instance_customer_id.delivered)
        self.assertEquals(
            set(
                self.env['round.instance.customer'].search(
                    [('delivery_round_id', '=', self.delivery_round_1.id),
                     ('delivered', '=', True),
                     ]
                ).ids
            ),
            {pstate0.instance_customer_id.id}
        )

        pstate1.deliver(new_cr=False)
        self.assertTrue(pstate1.instance_customer_id.delivered)
        self.assertEquals(
            set(
                self.env['round.instance.customer'].search(
                    [('delivery_round_id', '=', self.delivery_round_1.id),
                     ('delivered', '=', True),
                     ]
                ).ids
            ),
            {pstate0.instance_customer_id.id,
             pstate1.instance_customer_id.id},
        )

        pstate2.deliver(new_cr=False)
        self.assertTrue(pstate2.instance_customer_id.delivered)
        self.assertEquals(
            set(
                self.env['round.instance.customer'].search(
                    [('delivery_round_id', '=', self.delivery_round_1.id),
                     ('delivered', '=', True),
                     ]
                ).ids
            ),
            {pstate0.instance_customer_id.id,
             pstate1.instance_customer_id.id,
             pstate2.instance_customer_id.id,
             },
        )
