# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestTimeLimitOrder(TransactionCase):
    post_install = False
    at_install = True

    def setUp(self):
        super(TestTimeLimitOrder, self).setUp()

        self.env['round.template.version'].search([]).write(
            {'is_default_version': False}
        )

        # Set all round instance to done to be sure that
        # there are no other active instance
        self.env['round.instance'].search([]).write({'state': 'done'})

        self.partner = self.env['res.partner'].create(
            {'name': 'Partner test', 'ref': '982492834234'}
        )
        self.itinerary = self.env['round.itinerary'].create(
            {'name': 'Itinerary test', 'code': 'test', 'sequence': 1}
        )
        self.position = self.env['round.itinerary.position'].create(
            {
                'itinerary_id': self.itinerary.id,
                'sequence': 1,
                'partner_id': self.partner.id,
            }
        )
        self.template = self.env['round.template'].create(
            {
                'code': 'TEST',
                'name': 'Test template',
                'itinerary_ids': [(6, 0, [self.itinerary.id])],
                'time_picking_planned': 8,
            }
        )

    def test_01_compute_time_limit_order(self):
        """
        Test the method _compute_time_limit_order
        :return:
        """

        # Try without version on the template
        self.assertFalse(self.partner.time_limit_order)

        # Try without default version on the template
        version = self.env['round.template.version'].create(
            {'is_default_version': False, 'name': 'Version 1'}
        )

        self.template.write({'version_ids': [(4, version.id, 0)]})
        self.env.clear()
        self.assertFalse(self.partner.time_limit_order)

        # Try with a default version
        default_version = self.env['round.template.version'].create(
            {'is_default_version': True, 'name': 'Default version'}
        )

        self.template.write({'version_ids': [(4, default_version.id, 0)]})
        self.env.clear()
        self.assertEqual(self.partner.time_limit_order, 8)

        # Create a new template (time picking planned == 6 hour)
        itinerary_2 = self.env['round.itinerary'].create(
            {'name': 'Itinerary test', 'code': 'test', 'sequence': 1}
        )
        template_2 = self.env['round.template'].create(
            {
                'code': 'TEST 2',
                'name': 'Test 2 template',
                'itinerary_ids': [(6, 0, [itinerary_2.id])],
                'time_picking_planned': 6,
                'version_ids': [(4, default_version.id, 0)],
            }
        )
        self.env['round.itinerary.position'].create(
            {
                'itinerary_id': itinerary_2.id,
                'sequence': 1,
                'partner_id': self.partner.id,
            }
        )
        self.env.clear()
        self.assertEqual(self.partner.time_limit_order, 6)

        # Test if the time picking planned is 6.01, the time limit of order
        # must be 6
        template_2.write({'time_picking_planned': 6.01})
        self.env.clear()
        self.assertEqual(self.partner.time_limit_order, 6)

        # Test if the time picking planned is 6.29, the time limit of order
        # must be 6.25
        template_2.write({'time_picking_planned': 6.29})
        self.env.clear()
        self.assertEqual(self.partner.time_limit_order, 6.25)
