# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestPurchaseOrder(common.TransactionCase):

    def test_get_next_scheduled_date(self):
        """
        Calendar:
        - 31 december 2017: Saturday
        - 1 january 2017: Sunday
        - 2 january 2017: Monday
        - 3 january 2017: Tuesday
        - 4 january 2017: Wednesday
        - 5 january 2017: Thursday
        - 6 january 2017: Friday
        - 7 january 2017: Saturday
        - 8 january 2017: Sunday
        :return:
        """
        # Set the lead time to 3 days
        self.env['ir.config_parameter'].set_param('purchase.lead_time', 3)

        # Create a bank holiday
        bank_holiday = self.env['bank.holiday']
        bank_holiday.create({
            'name': '2 January',
            'date': '2017-01-02'
        })
        bank_holiday.create({
            'name': '9 January',
            'date': '2017-01-09'
        })

        pol = self.env['purchase.order.line']

        date_planned = pol.get_next_scheduled_date('2016-12-31')
        self.assertEqual(date_planned, '2017-01-05 00:00:00')

        date_planned = pol.get_next_scheduled_date('2017-01-02')
        self.assertEqual(date_planned, '2017-01-05 00:00:00')

        date_planned = pol.get_next_scheduled_date('2017-01-03')
        self.assertEqual(date_planned, '2017-01-06 00:00:00')

        date_planned = pol.get_next_scheduled_date('2017-01-06')
        self.assertEqual(date_planned, '2017-01-12 00:00:00')
