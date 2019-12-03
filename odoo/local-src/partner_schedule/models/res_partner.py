# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResPartner(models.Model):
    _inherit = 'res.partner'

    working_schedules_ids = fields.One2many(
        'partner.scheduled.week',
        'partner_id',
        string='Partner Schedule',
        ondelete="cascade",
    )

    def get_working_schedule_on_date(self, day):
        # return working schedule on some day
        # return false if no appropriate schedule
        if not self:
            return True
        self.ensure_one()
        return self.working_schedules_ids.filtered(
            lambda l: l.start_date <= day
            and (l.end_date >= day or not l.end_date)
        )

    def is_next_schedule(self, day):
        if self.get_next_schedule(day):
            return True

    def get_next_schedule(self, day):
        schedule_model = self.env['partner.scheduled.week']
        if self:
            return schedule_model.search(
                [('partner_id', '=', self.id), ('start_date', '>', day)],
                order='start_date ASC',
                limit=1,
            )
        else:
            schedule_model

    def get_next_shipping_date(self, day):
        date_format_day = fields.Date.from_string(day)
        schedule = self.get_working_schedule_on_date(day)
        str_day = date_format_day.strftime(DEFAULT_SERVER_DATE_FORMAT)
        counter = 1
        while schedule:
            while counter != 7:
                if schedule._is_shipping_date_allowed(str_day):
                    return date_format_day
                date_format_day += datetime.timedelta(days=1)
                str_day = date_format_day.strftime(DEFAULT_SERVER_DATE_FORMAT)
                counter += 1
                # find current schedule
                if self.get_working_schedule_on_date(str_day) != schedule:
                    schedule = self.get_working_schedule_on_date(str_day)
                    counter = 1
            if self.is_next_schedule(str_day):
                schedule = self.get_next_schedule(str_day)
                counter = 1
                continue
            if not schedule.end_date:
                # week are checked for available days and there is no new
                # schedule or period without schedule
                raise UserError(
                    _(
                        u'No available days found for schedule {} from {}'
                    ).format(schedule.name, schedule.start_date)
                )
            else:
                # no more schedule to check switch to the end of current
                date_format_day = fields.Date.from_string(
                    schedule.end_date
                ) + datetime.timedelta(days=1)
                break
        # if no any schedule found return current date as acceptable
        return date_format_day

    def is_shipping_date_allowed(self, day):
        schedule = self.get_working_schedule_on_date(day)
        return schedule._is_shipping_date_allowed(day)
