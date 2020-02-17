# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestRoundTags(SavepointCase):
    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super(TestRoundTags, cls).setUpClass()

        # Set all round instance to done to be sure that
        # there are no other active instance
        cls.env['round.instance'].search([]).write({'state': 'done'})

        round_tag = cls.env['round.tag']
        cls.tag_monday = round_tag.create({'name': 'Monday'})
        cls.tag_friday = round_tag.create({'name': 'Friday'})

        cls.partner = cls.env['res.partner'].create(
            {'name': 'Partner test', 'ref': '00099876743567'}
        )
        cls.itinerary = cls.env['round.itinerary'].create(
            {'name': 'Itinerary test', 'code': 'test', 'sequence': 1}
        )
        cls.position = cls.env['round.itinerary.position'].create(
            {
                'itinerary_id': cls.itinerary.id,
                'sequence': 1,
                'partner_id': cls.partner.id,
            }
        )
        cls.template = cls.env['round.template'].create(
            {
                'code': 'TEST',
                'name': 'Test template',
                'itinerary_ids': [(6, 0, [cls.itinerary.id])],
            }
        )

        # delivery rounds shouldn't overlap on the next day
        # so to have consistent tests we will have round instances
        # at 1 hour and 5 hours from 7 hour in the morning
        cls.virtual_now = datetime.now().replace(hour=7)
        picking_planned = cls.virtual_now + relativedelta(hours=3)
        cls.instance = cls.env['round.instance'].create(
            {
                'template_id': cls.template.id,
                'date': fields.Date.to_string(picking_planned),
                'time_picking_planned': picking_planned.hour,
                'time_leave_planned': 10,
                'state': 'draft',
                'itinerary_ids': [(6, 0, [cls.itinerary.id])],
            }
        )

    def test_01_find_bypartner(self):
        """
        Test the method find_bypartner (to find the best delivery instance)
        :return:
        """
        instance_obj = self.env['round.instance']

        # Test simple case (without tags)
        instance = instance_obj.find_bypartner(self.partner)
        self.assertEqual(instance, self.instance)

        # Add the tag monday on the instance
        self.instance.write({'tag_ids': [(6, 0, [self.tag_monday.id])]})
        instance = instance_obj.find_bypartner(self.partner)
        self.assertEqual(instance, self.instance)

        # Add the tag friday on the customer position
        # => Not instance can be found
        # The instance test contains only the flag "Monday"
        self.position.write({'tag_ids': [(6, 0, [self.tag_friday.id])]})
        instance = instance_obj.find_bypartner(self.partner)
        self.assertFalse(instance)

        # Add the flag friday on the instance
        self.instance.write({'tag_ids': [(4, self.tag_friday.id, 0)]})
        instance = instance_obj.find_bypartner(self.partner)
        self.assertEqual(instance, self.instance)

    def test_02_find_bypartner(self):
        """
        Test the method find_bypartner on delivery with several instance
        and if the method sort correctly instance
        :return:
        """
        instance_obj = self.env['round.instance']

        # Create the best itinerary (picking planned = now + 1 hours)
        # By default this itinerary must be taken
        picking_planned = self.virtual_now + relativedelta(hours=1)
        best_itinerary = self.env['round.itinerary'].create(
            {'name': 'Best itinerary', 'code': 'best', 'sequence': 1}
        )
        best_position = self.env['round.itinerary.position'].create(
            {
                'itinerary_id': best_itinerary.id,
                'sequence': 1,
                'partner_id': self.partner.id,
            }
        )
        self.template.write({'itinerary_ids': [(4, best_itinerary.id, 0)]})
        best_instance = self.env['round.instance'].create(
            {
                'template_id': self.template.id,
                'date': fields.Date.to_string(picking_planned),
                'time_picking_planned': picking_planned.hour,
                'time_leave_planned': 7,
                'state': 'draft',
                'itinerary_ids': [(6, 0, [best_itinerary.id])],
            }
        )

        # Create the worst itinerary (picking planned = now + 5 hours)
        worst_itinerary = self.env['round.itinerary'].create(
            {'name': 'Worst itinerary', 'code': 'worst', 'sequence': 1}
        )
        worst_position = self.env['round.itinerary.position'].create(
            {
                'itinerary_id': worst_itinerary.id,
                'sequence': 1,
                'partner_id': self.partner.id,
            }
        )
        self.template.write({'itinerary_ids': [(4, worst_itinerary.id, 0)]})
        picking_planned = self.virtual_now + relativedelta(hours=5)
        worst_instance = self.env['round.instance'].create(
            {
                'template_id': self.template.id,
                'date': fields.Date.to_string(picking_planned),
                'time_picking_planned': picking_planned.hour,
                'time_leave_planned': 11,
                'state': 'draft',
                'itinerary_ids': [(6, 0, [worst_itinerary.id])],
            }
        )

        # The "best itinerary" has a better picking time
        # (picking planned = now + 1 hours)
        instance = instance_obj.find_bypartner(self.partner)
        self.assertEqual(instance, best_instance)

        # Add the flag monday on the customer position for all itineraries
        # and add the flag friday on the best instance and on the test instance
        # Now the best instance and the test instance cannot be taken
        self.position.write({'tag_ids': [(6, 0, [self.tag_monday.id])]})
        best_position.write({'tag_ids': [(6, 0, [self.tag_monday.id])]})
        worst_position.write({'tag_ids': [(6, 0, [self.tag_monday.id])]})
        self.instance.write({'tag_ids': [(6, 0, [self.tag_friday.id])]})
        best_instance.write({'tag_ids': [(6, 0, [self.tag_friday.id])]})
        # We set the flag "Monday" on the worst instance
        worst_instance.write({'tag_ids': [(6, 0, [self.tag_monday.id])]})

        instance = instance_obj.find_bypartner(self.partner)
        self.assertEqual(instance, worst_instance)

        # Add the flag friday on the customer position
        best_position.write({'tag_ids': [(4, self.tag_friday.id), 0]})
        instance = instance_obj.find_bypartner(self.partner)
        self.assertEqual(instance, best_instance)
