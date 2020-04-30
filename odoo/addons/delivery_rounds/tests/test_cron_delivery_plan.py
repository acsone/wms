# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase

ISO_WEEK_DAY_MONDAY = 1


class TestCronDeliveryPlan(TransactionCase):
    post_install = False
    at_install = True

    def setUp(self):
        super(TestCronDeliveryPlan, self).setUp()

        self.version = self.env['round.template.version'].create(
            {
                'name': 'Version test',
                'template_ids': [
                    (
                        0,
                        0,
                        {
                            'name': 'Round template test',
                            'code': 'TEST',
                            'time_picking_planned': 8,
                            'time_leave_planned': 9,
                        },
                    )
                ],
            }
        )

    def test_01_cron_delivery_plan(self):
        """
        Test if the method _compute_next_execution correctly compute
        the next execution
        :return:
        """
        cron_delivery_plan = self.env['cron.delivery.plan']

        tomorrow = datetime.today() + relativedelta(days=1)

        next_monday = tomorrow
        while next_monday.isoweekday() != ISO_WEEK_DAY_MONDAY:
            next_monday += relativedelta(days=1)
        next_monday_str = fields.Date.to_string(next_monday)

        # Try with a day of week
        cron_1 = cron_delivery_plan.create(
            {'week_day': ISO_WEEK_DAY_MONDAY, 'version_id': self.version.id}
        )
        self.assertEqual(cron_1.next_execution, next_monday_str)

        # Try with a date
        cron_2 = cron_delivery_plan.create(
            {'date_overwrite': next_monday_str, 'version_id': self.version.id}
        )
        self.assertEqual(cron_2.next_execution, next_monday_str)

        cron_delivery_plan.with_context(
            {'assign_moves': False}
        ).create_daily_plan(today_overwrite=next_monday_str)

        # The next execution of cron 1 (with day of week) should be one week
        # late
        next_week = next_monday + relativedelta(days=7)
        next_week_str = fields.Date.to_string(next_week)
        self.assertEqual(cron_1.next_execution, next_week_str)

        # The cron 2 should be deactivate because this cron was a single shot
        self.assertFalse(cron_2.active)
