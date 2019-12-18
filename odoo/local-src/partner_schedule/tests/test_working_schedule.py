# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from .common import TestCustomerWorkingScheduleBase


class TestCustomerWorkingSchedule(TestCustomerWorkingScheduleBase):
    def test_scheduled_forbided_periods_1(self):
        # already have schedule on this date

        # | 2019.01.01          2019.01.31   |
        # | ------------------------------   |
        # |       2019.01.15                 |
        # |       ---------------------------|

        with self.assertRaises(ValidationError):
            # open period
            self.create_schedule(
                {'start_date': '2019-01-15', 'end_date': False}
            )

    def test_scheduled_forbided_time_2(self):
        # same as previous, check if triggered with end_date

        # | 2019.01.01          2019.01.31 |
        # | -------------------------------|
        # |     2019.01.15 2019.01.17      |
        # |          ---------             |
        with self.assertRaises(ValidationError):
            self.create_schedule(
                {'start_date': '2019-01-15', 'end_date': '2019-01-17'}
            )

    def test_scheduled_forbided_periods_3(self):
        # cannot create schedule without defined end date in before period

        # |              2019.01.01     2019.01.31 |
        # |              --------------------------|
        # |  2018.01.01                            |
        # |  ---------------------------------     |
        with self.assertRaises(ValidationError):
            self.create_schedule(
                {'start_date': '2018-01-01', 'end_date': False}
            )

    def test_scheduled_forbided_periods_4(self):
        # cannot create schedule without defined end date in before period

        # |  2019.01.01                         |
        # |  ------------------------------     |
        # |              2019.11.01             |
        # |              -----------------------|

        self.graphic_1.end_date = False
        with self.assertRaises(ValidationError):
            self.create_schedule(
                {'start_date': '2019-11-01', 'end_date': False}
            )

    def test_scheduled_forbided_periods_5(self):
        # | 2019.01.01      2019.01.31           |
        # | --------------------------           |
        # |           2019.01.15      2019.03.03 |
        # |           -------------------------- |

        with self.assertRaises(ValidationError):
            self.create_schedule(
                {'start_date': '2019-01-15', 'end_date': '2019-03-03'}
            )

    def test_scheduled_forbided_periods_6(self):
        # |       2019.01.01      2019.01.31         |
        # |       --------------------------         |
        # |  2018.01.01                2019.03.03    |
        # |  ------------------------------------    |

        with self.assertRaises(ValidationError):
            self.create_schedule(
                {'start_date': '2018-01-01', 'end_date': '2019-03-03'}
            )

    def test_scheduled_allowed_periods(self):
        # can create in past period if end_date defined and valid

        # |                        2019.01.01    2019.01.31 |
        # |                        ------------------------ |
        # | 2018.01.01 2018.01.31                           |
        # | ---------------------                           |
        self.create_schedule(
            {'start_date': '2018-01-01', 'end_date': '2018-01-31'}
        )

        # can create open schedule after

        # | 2019.01.01     2019.01.31                 |
        # | -------------------------                 |
        # |                           2020.03.01      |
        # |                           ----------------|

        self.create_schedule({'start_date': '2020-03-01', 'end_date': False})

    def test_allowed_day(self):
        # before start date schedule are not applied
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-04-29'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-04-30'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-05-01'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-05-02'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-05-03'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-05-04'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2018-05-05'))
        # check on schedule period
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-01-01'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-01-02'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-01-03'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-01-04'))
        # holidays are not allowed
        self.assertFalse(self.partner.is_shipping_date_allowed('2019-01-05'))
        self.assertFalse(self.partner.is_shipping_date_allowed('2019-01-06'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-01-07'))
        # after end date schedule are not applied anymore
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-01'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-02'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-03'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-04'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-05'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-06'))
        self.assertTrue(self.partner.is_shipping_date_allowed('2019-02-07'))

    def test_next_allowed_day(self):
        # if requested date is ok return it
        self.assertEqual(
            self.partner.get_next_shipping_date('2019-01-03').strftime(
                DEFAULT_SERVER_DATE_FORMAT
            ),
            '2019-01-03',
        )
        # requested date forbiden, find next allowed date
        self.assertEqual(
            self.partner.get_next_shipping_date('2019-01-05').strftime(
                DEFAULT_SERVER_DATE_FORMAT
            ),
            '2019-01-07',
        )
        self.graphic_1.day_4 = True
        # requested date forbiden, schedule period is over, return first
        # date after schedule is over
        self.assertEqual(
            self.partner.get_next_shipping_date('2019-01-31').strftime(
                DEFAULT_SERVER_DATE_FORMAT
            ),
            '2019-02-01',
        )
        # create new schedule which forbits 2019-02-01
        self.create_schedule(
            {
                'start_date': '2019-02-01',
                'end_date': '2019-02-28',
                'day_1': True,
                'day_5': True,
                'day_6': True,
                'day_7': True,
            }
        )
        # iterate on schedules till available date will be found
        self.assertEqual(
            self.partner.get_next_shipping_date('2019-01-31').strftime(
                DEFAULT_SERVER_DATE_FORMAT
            ),
            '2019-02-05',
        )
        # no any schedule for this period, return current date
        self.assertEqual(
            self.partner.get_next_shipping_date('2019-05-04').strftime(
                DEFAULT_SERVER_DATE_FORMAT
            ),
            '2019-05-04',
        )

    def test_no_allowed_day(self):
        self.graphic_1.write(
            {
                'day_1': True,
                'day_2': True,
                'day_3': True,
                'day_4': True,
                'day_5': True,
                'end_date': False,
            }
        )
        # all days are forbiden no end date for this schedule
        with self.assertRaises(UserError):
            self.partner.get_next_shipping_date('2019-01-03')
        self.graphic_1.write({'end_date': '2019-02-28'})
        self.assertEqual(
            self.partner.get_next_shipping_date('2019-01-03').strftime(
                DEFAULT_SERVER_DATE_FORMAT
            ),
            '2019-03-01',
        )

    def test_get_right_schedule(self):
        self.create_schedule(
            {
                'start_date': '2019-02-01',
                'end_date': '2019-02-28',
                'day_1': True,
            }
        )
        schedule = self.partner.get_next_schedule('2017-01-01')
        self.assertEqual(schedule.start_date, '2019-01-01')
