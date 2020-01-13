# -*- coding: utf-8 -*-
# Copyright 2019 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PartnerManagedDays(models.Model):
    _name = 'partner.scheduled.week'
    _description = 'Partner non working days'
    _order = "start_date desc"

    name = fields.Char(string='Label')
    start_date = fields.Date(
        string='Start date',
        required='True',
        help="To mark only one day set same date as start and end date",
    )
    end_date = fields.Date(string='End date', required='True')
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
            self.env.cr.execute(
                '''
                    SELECT id
                    FROM partner_scheduled_week
                    WHERE start_date <= %s AND end_date >= %s
                        AND partner_id=%s
                        AND id <> %s''',
                (
                    schedule.end_date,
                    schedule.start_date,
                    schedule.partner_id.id,
                    schedule.id,
                ),
            )
            if any(self.env.cr.fetchall()):
                raise ValidationError(
                    _('You cannot have 2 schedules that overlap!.')
                )
