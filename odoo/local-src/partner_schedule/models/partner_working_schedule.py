# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ScheduledWeekDays(models.Model):
    _name = 'scheduled.week.days'
    _description = 'Non working days'

    day_1 = fields.Boolean('Monday')
    day_2 = fields.Boolean('Tuesday')
    day_3 = fields.Boolean('Wednesday')
    day_4 = fields.Boolean('Thursday')
    day_5 = fields.Boolean('Friday')
    day_6 = fields.Boolean('Saturday')
    day_7 = fields.Boolean('Sunday')


class PartnerManagedDays(models.Model):
    _name = 'partner.scheduled.week'
    _inherit = ['scheduled.week.days']
    _description = 'Partner non working days'
    _order = "start_date desc"

    name = fields.Char(string='Label')
    start_date = fields.Date(string='Start date', required='True')
    end_date = fields.Date(string='End date')
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required='True'
    )

    @api.constrains('start_date', 'end_date')
    def _check_closing_date(self):
        for rec in self:
            if rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError(
                    _(
                        'The end date of a schedule must be after the start '
                        'date or empty'
                    )
                )

    @api.constrains('start_date', 'end_date', 'partner_id')
    def _check_schedule_period(self):
        for schedule in self:
            condition, params = schedule._prepare_date_condition()
            params += (schedule.partner_id.id, schedule.id)
            self.env.cr.execute(
                '''
                    SELECT id
                    FROM partner_scheduled_week
                    WHERE '''
                + condition
                + '''
                        AND partner_id=%s
                        AND id <> %s''',
                (params),
            )
            if any(self.env.cr.fetchall()):
                raise ValidationError(
                    _('You cannot have 2 schedules that overlap!.')
                )

    def _prepare_date_condition(self):
        self.ensure_one()
        if self.end_date:
            condition = "start_date <= %s AND end_date >= %s"
            params = (self.end_date, self.start_date)
        else:
            condition = "(end_date >= %s OR end_date IS NULL)"
            params = (self.start_date,)
        return (condition, params)

    def _is_shipping_date_allowed(self, day):
        weekday = fields.Date.from_string(day).weekday() + 1
        return not getattr(self, 'day_' + str(weekday))
