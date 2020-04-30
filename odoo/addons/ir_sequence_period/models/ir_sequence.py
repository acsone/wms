# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    use_end_date = fields.Boolean(
        'Use the end date of the range',
        help="""By default Odoo will use
                                  the start date (from) to compute date
                                  with the prefix range_ (eg: range_year).

                                  If you set this flag Odoo will use the end
                                  date (to) to compute date with
                                  the prefix range.
                                  Eg: From 1/10/2016 to 31/9/2017
                                  without the flag:
                                  %(range_year)s => 2016
                                  with the flag
                                  %(range_year)s => 2017
                                  """,
    )

    def _create_date_range_seq(self, date_string):
        user = self.env.user
        date = fields.Date.from_string(date_string)
        if 'range_month' in self.prefix:
            start = date.replace(day=1)
            end = start + relativedelta(months=+1, days=-1)
        elif 'range_year' in self.prefix:
            ld = user.company_id.fiscalyear_last_day
            lm = user.company_id.fiscalyear_last_month
            start = end = date.replace(day=ld, month=lm)
            start += relativedelta(days=+1)
            if start <= date:
                end += relativedelta(years=+1)
            else:
                start -= relativedelta(years=+1)
        return (
            self.env['ir.sequence.date_range']
            .sudo()
            .create(
                {
                    'date_from': fields.Date.to_string(start),
                    'date_to': fields.Date.to_string(end),
                    'sequence_id': self.id,
                }
            )
        )


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    def _next(self):
        self.ensure_one()

        if self.sequence_id.use_end_date:
            return super(
                IrSequenceDateRange,
                self.with_context(ir_sequence_date_range=self.date_to),
            )._next()

        return super(IrSequenceDateRange, self)._next()
