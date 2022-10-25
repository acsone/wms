# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MixinPast(models.AbstractModel):
    """Adds 'is_past' and 'is_future' fields, using existing date_start/end fields."""

    _name = "mixin.past"

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
        reference_date = reference_date or fields.Date.context_today(self)
        if isinstance(reference_date, str):
            reference_date = fields.Date.from_string(reference_date)
        if isinstance(maybe_date_end, str):
            maybe_date_end = fields.Date.from_string(maybe_date_end)
        return maybe_date_end < reference_date

    @api.model
    def _is_future_date(self, maybe_date_start, reference_date=False):
        if not maybe_date_start:
            return False
        reference_date = reference_date or fields.Date.context_today(self)
        if isinstance(reference_date, str):
            reference_date = fields.Date.from_string(reference_date)
        if isinstance(maybe_date_start, str):
            maybe_date_start = fields.Date.from_string(maybe_date_start)
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
        result_operator = "<"
        if (not value and operator == "=") or (value and operator == "!="):
            result_operator = ">"
        return [("date_end", result_operator, today)]

    def _search_is_future(self, operator, value):
        today = fields.Date.context_today(self)
        result_operator = ">"
        if (not value and operator == "=") or (value and operator == "!="):
            result_operator = "<"
        return [("date_start", result_operator, today)]
