# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MixinPast(models.AbstractModel):
    """Adds an 'is_past' field, computed using an existing date_end field."""

    _name = "mixin.past"

    is_past = fields.Boolean(compute="_compute_is_past", store=False)

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

    @api.depends("date_end")
    def _compute_is_past(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.is_past = self._is_past_date(record.date_end, today)
