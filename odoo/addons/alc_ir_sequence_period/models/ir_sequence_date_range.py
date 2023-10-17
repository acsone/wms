# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.models.ir_sequence import (
    IrSequenceDateRange as IrSequenceDateRangeBase,
)


class IrSequenceDateRange(IrSequenceDateRangeBase):
    def _next(self):
        self.ensure_one()
        if self.sequence_id.use_end_date:
            return super(
                IrSequenceDateRange,
                self.with_context(ir_sequence_date_range=self.date_to),
            )._next()
        return super()._next()
