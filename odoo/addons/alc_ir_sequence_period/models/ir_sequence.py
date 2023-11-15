# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.base.models.ir_sequence import IrSequence as IrSequenceBase


class IrSequence(IrSequenceBase):
    use_end_date = fields.Boolean(
        "Use the end date of the range",
        help="""By default Odoo will use the start date (from) to compute date with the
        prefix range_ (eg: range_year). If you set this flag Odoo will use the end date
        (to) to compute date with the prefix range. Eg: From 1/10/2016 to 31/9/2017
        without the flag: %(range_year)s => 2016 with the flag %(range_year)s => 2017""",
    )

    def _create_date_range_seq(self, date_string):
        """Create the date range using company fiscal year date end."""
        user = self.env.user
        date = fields.Date.from_string(date_string)
        if "range_month" in self.prefix:
            start = date.replace(day=1)
            end = start + relativedelta(months=+1, days=-1)
        elif "range_year" in self.prefix:
            ld = user.company_id.fiscalyear_last_day
            lm = int(user.company_id.fiscalyear_last_month)
            start = end = date.replace(day=ld, month=lm)
            start += relativedelta(days=+1)
            if start <= date:
                end += relativedelta(years=+1)
            else:
                start -= relativedelta(years=+1)
        return (
            self.env["ir.sequence.date_range"]
            .sudo()
            .create(
                {
                    "date_from": fields.Date.to_string(start),
                    "date_to": fields.Date.to_string(end),
                    "sequence_id": self.id,
                }
            )
        )
