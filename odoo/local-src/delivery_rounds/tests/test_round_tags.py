# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestRoundTags(TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestRoundTags, self).setUp()

        self.env['round.instance'].search([]).write({
            'state': 'done',
        })

        round_tag = self.env['round.tag']
        self.tag_monday = round_tag.create({
            'name': 'Monday'
        })
        self.tag_friday = round_tag.create({
            'name': 'Friday'
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Partner test'
        })
        self.itinerary = self.env['round.itinerary'].create({
            'name': 'Itinerary test',
            'code': 'test',
            'sequence': 10,
        })
        self.position = self.env['round.itinerary.position'].create({
            'itinerary_id': self.itinerary.id,
            'sequence': 1,
            'partner_id': self.partner.id,
        })
        self.template = self.env['round.template'].create({
            'code': 'TEST',
            'name': 'Test template',
            'itinerary_ids': [(6, 0, [self.itinerary.id])]
        })
        self.instance = self.env['round.instance'].create({
            'template_id': self.template.id,
            'date': fields.Date.today(),
            'time_picking_planned': 8,
            'time_leave_planned': 10,
            'name': 'Instance test',
            'state': 'draft',
            'itinerary_ids': [(6, 0, [self.itinerary.id])]
        })

    def test_01_find(self):
        """
        Test the method find (to find the best delivery instance)
        :return:
        """
        instance_obj = self.env['round.instance']

        # Test simple case (without tags)
        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, self.instance)

        # Add the tag monday on the instance
        self.instance.write({
            'tag_ids': [(6, 0, [self.tag_monday.id])]
        })
        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, self.instance)

        # Add the tag friday on the customer position
        # => Not instance can be found
        # The instance test contains only the flag "Monday"
        self.position.write({
            'tag_ids': [(6, 0, [self.tag_friday.id])]
        })
        instance = instance_obj.find(self.partner)
        self.assertFalse(instance)

        # Add the flag friday on the instance
        self.instance.write({
            'tag_ids': [(4, self.tag_friday.id, 0)]
        })
        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, self.instance)

    def test_02_find(self):
        """
        Test the method find on delivery with several instance
        and if the method sort correctly instance
        :return:
        """
        instance_obj = self.env['round.instance']

        # Create the best itinerary (sequence 5)
        # By default this itinerary must be taken
        best_itinerary = self.env['round.itinerary'].create({
            'name': 'Best itinerary',
            'code': 'best',
            'sequence': 5,
        })
        best_position = self.env['round.itinerary.position'].create({
            'itinerary_id': best_itinerary.id,
            'sequence': 1,
            'partner_id': self.partner.id,
        })
        self.template.write({
            'itinerary_ids': [(4, best_itinerary.id, 0)]
        })
        best_instance = self.env['round.instance'].create({
            'template_id': self.template.id,
            'date': fields.Date.today(),
            'time_picking_planned': 6,
            'time_leave_planned': 7,
            'name': 'Best instance',
            'state': 'draft',
            'itinerary_ids': [(6, 0, [best_itinerary.id])]
        })

        # Create the worst itinerary (sequence 50)
        worst_itinerary = self.env['round.itinerary'].create({
            'name': 'Worst itinerary',
            'code': 'worst',
            'sequence': 50,
        })
        worst_position = self.env['round.itinerary.position'].create({
            'itinerary_id': worst_itinerary.id,
            'sequence': 1,
            'partner_id': self.partner.id,
        })
        self.template.write({
            'itinerary_ids': [(4, worst_itinerary.id, 0)]
        })
        worst_instance = self.env['round.instance'].create({
            'template_id': self.template.id,
            'date': fields.Date.today(),
            'time_picking_planned': 10,
            'time_leave_planned': 11,
            'name': 'Worst instance',
            'state': 'draft',
            'itinerary_ids': [(6, 0, [worst_itinerary.id])]
        })

        # The "best itinerary" has the best sequence
        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, best_instance)

        # Add the flag monday on the customer position for all itineraries
        # and add the flag friday on the best instance and on the test instance
        # Now the best instance and the test instance cannot be taken
        self.position.write({
            'tag_ids': [(6, 0, [self.tag_monday.id])]
        })
        best_position.write({
            'tag_ids': [(6, 0, [self.tag_monday.id])]
        })
        worst_position.write({
            'tag_ids': [(6, 0, [self.tag_monday.id])]
        })
        self.instance.write({
            'tag_ids': [(6, 0, [self.tag_friday.id])]
        })
        best_instance.write({
            'tag_ids': [(6, 0, [self.tag_friday.id])]
        })
        # We set the flag "Monday" on the worst instance
        worst_instance.write({
            'tag_ids': [(6, 0, [self.tag_monday.id])]
        })

        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, worst_instance)

        # Add the flag friday on the customer position
        best_position.write({
            'tag_ids': [(4, self.tag_friday.id), 0]
        })
        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, best_instance)
