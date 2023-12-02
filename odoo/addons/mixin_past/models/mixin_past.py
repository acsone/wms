# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.osv.expression import FALSE_LEAF, NEGATIVE_TERM_OPERATORS, TRUE_LEAF


class MixinPast(models.AbstractModel):
    """Adds 'is_past' and 'is_future' fields, using existing date_start/end fields."""

    _name = "mixin.past"
    _description = "Mixin Past"

    is_past = fields.Boolean(
        compute="_compute_is_past", search="_search_is_past", store=False
    )
    is_future = fields.Boolean(
        compute="_compute_is_future", search="_search_is_future", store=False
    )

    @api.model
    def _is_past_date(self, maybe_date_end, reference_date=False):
        if not maybe_date_end:
            return False
        maybe_date_end = fields.Date.to_date(maybe_date_end)
        if reference_date:
            reference_date = fields.Date.to_date(reference_date)
        else:
            reference_date = fields.Date.context_today(self)
        return maybe_date_end < reference_date

    @api.model
    def _is_future_date(self, maybe_date_start, reference_date=False):
        if not maybe_date_start:
            return False
        maybe_date_start = fields.Date.to_date(maybe_date_start)
        if reference_date:
            reference_date = fields.Date.to_date(reference_date)
        else:
            reference_date = fields.Date.context_today(self)
        return maybe_date_start > reference_date

    @api.depends("date_end")
    def _compute_is_past(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.is_past = self._is_past_date(record.date_end, today)

    @api.depends("date_start")
    def _compute_is_future(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.is_future = self._is_future_date(record.date_start, today)

    def _search_is_past(self, operator, value):
        today = fields.Date.context_today(self)
        domain = []
        negative_op = operator in NEGATIVE_TERM_OPERATORS
        is_past = (value and not negative_op) or (not value and negative_op)
        if "in" in operator:  # value should be a list
            if not value:
                domain = TRUE_LEAF if negative_op else FALSE_LEAF
            elif True in value and False in value:
                domain = FALSE_LEAF if negative_op else TRUE_LEAF
            elif False in value:  # not in [False]
                is_past = negative_op
            else:  # in [True]
                is_past = not negative_op
        if not domain:
            if is_past:
                domain = domain or [("date_end", "<", today)]
            else:
                domain = ["|", ("date_end", ">", today), ("date_end", "=", False)]
        return domain

    def _search_is_future(self, operator, value):
        today = fields.Date.context_today(self)
        domain = []
        negative_op = operator in NEGATIVE_TERM_OPERATORS
        is_future = (value and not negative_op) or (not value and negative_op)
        if "in" in operator:  # value should be a list
            if not value:
                domain = TRUE_LEAF if negative_op else FALSE_LEAF
            elif True in value and False in value:
                domain = FALSE_LEAF if negative_op else TRUE_LEAF
            elif False in value:  # not in [False]
                is_future = negative_op
            else:  # in [True]
                is_future = not negative_op
        if not domain:
            if is_future:
                domain = domain or [("date_start", ">", today)]
            else:
                domain = ["|", ("date_start", "<", today), ("date_start", "=", False)]
        return domain
