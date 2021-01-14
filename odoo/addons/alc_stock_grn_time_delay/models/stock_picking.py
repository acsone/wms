# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import numpy as np

from odoo import api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS


class StockPicking(models.Model):
    _inherit = "stock.picking"

    time_delay = fields.Integer(compute="_compute_time_delay", readonly=True, default=0)
    is_time_exceeded = fields.Boolean(
        default=False,
        compute="_compute_is_time_exceeded",
        search="_search_is_time_exceeded",
    )

    @api.depends("grn_date")
    def _compute_time_delay(self):
        today = datetime.today().strftime("%Y-%m-%d")
        for rec in self:
            if rec.grn_date:
                time = rec.grn_date.split(" ")[0]
                rec.time_delay = np.busday_count(time, today)

    @api.depends("time_delay")
    def _compute_is_time_exceeded(self):
        max_time = self.env[
            "stock.config.settings"
        ].get_max_delay_to_process_receipt_config()
        for rec in self:
            if rec.time_delay >= max_time:
                rec.is_time_exceeded = True

    def _search_is_time_exceeded(self, operator, value):
        max_time = self.env[
            "stock.config.settings"
        ].get_max_delay_to_process_receipt_config()
        search_time_exceeded = (
            # is_time_exceeded != False
            (operator in NEGATIVE_TERM_OPERATORS and not value)
            or
            # is_time_exceeded = True
            (operator not in NEGATIVE_TERM_OPERATORS and value)
        )

        date = datetime.now() - timedelta(days=max_time)
        min_date = date.strftime("%Y-%m-%d %H:%M:%S")
        if search_time_exceeded:
            return [("grn_date", "<=", min_date)]
        return ["|", ("grn_date", "=", False), ("grn_date", ">", min_date)]
