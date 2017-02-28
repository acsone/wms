# -*- coding: utf-8 -*-
# Copyright 2016 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    use_end_date = fields.Boolean('Use the end date of the range',
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
                                  """)


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    def _next(self):
        self.ensure_one()

        if self.sequence_id.use_end_date:
            return super(IrSequenceDateRange, self.with_context(
                ir_sequence_date_range=self.date_to))._next()

        return super(IrSequenceDateRange, self)._next()
