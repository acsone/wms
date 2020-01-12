# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class TestCustomerWorkingScheduleBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCustomerWorkingScheduleBase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.schedule = cls.env['partner.scheduled.week']
        cls.partner = cls.env['res.partner'].create(
            {'name': 'Unittest partner', 'ref': '12344566777878'}
        )
        cls.graphic_1 = cls.create_schedule()

    @classmethod
    def create_schedule(cls, vals=None):
        default_values = {
            'partner_id': cls.partner.id,
            'name': 'Schedule 1',
            'start_date': '2019-01-01',
            'end_date': '2019-01-31',
        }
        if vals:
            default_values.update(vals)
        return cls.schedule.create(default_values)

    def test_allowed_day(self):

        # before start date schedule are not applied
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-05-05'))
        # holidays are not allowed
        self.assertFalse(self.partner.is_shipping_date_allowed('2019-01-01'))
        self.assertFalse(self.partner.is_shipping_date_allowed('2019-01-25'))
        self.assertFalse(self.partner.is_shipping_date_allowed('2019-01-31'))
        # after end date schedule are not applied anymore
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-01'))
