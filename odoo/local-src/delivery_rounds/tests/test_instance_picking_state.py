# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import DeliveryRoundTestCase


class TestInstancePickingState(DeliveryRoundTestCase):
    def test_picking_state_deliver_job(self):
        """Job that process a round.instance.picking.state"""
        ship1 = self._create_picking_out()
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
            set(
                self.delivery_round_1.instance_customer_ids.mapped(
                    'picking_ids'
                )
            ),
            {pick1},
        )

    def test_round_delivered(self):
        """Test that after round is delivered, the customer instances are deleted"""
        self.assertEqual(self.delivery_round_1.state, 'pending')
        pick = self._create_picking_pick(partner=self.partner2)
        ship = self._create_picking_out(self.partner2)

        pick.move_lines.write({'state': 'assigned'})

        ship.move_lines.write({'state': 'waiting'})

        pickings = pick | ship
        self.delivery_round_1._assign_pickings(pickings)

        self.assertEqual(len(self.delivery_round_1.instance_customer_ids), 1)

        with self.mock_with_delay() as (__, __):
            self.delivery_round_1.button_deliver()

        self.delivery_round_1.instance_customer_ids._deliver_job()
        self.assertEqual(len(self.delivery_round_1.instance_customer_ids), 0)
