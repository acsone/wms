# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestRoundTags(TransactionCase):

    def setUp(self):
        super(TestRoundTags, self).setUp()

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
            'sequence': 1,
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
        })

    def test_find(self):
        """
        Test the method find (to find the best delivery instance)
        :return:
        """
        instance_obj = self.env['round.instance']

        # Test simple case (without tags)
        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, self.instance)

        # Add the tag monday and friday on instance
        self.instance.write({
            'tag_ids': [(6, 0, [self.tag_monday.id, self.tag_friday.id])]
        })
        instance = instance_obj.find(self.partner)
        self.assertEqual(instance, self.instance)
