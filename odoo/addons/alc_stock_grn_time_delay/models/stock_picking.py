# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import numpy

from odoo import api, fields
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):

    time_delay = fields.Integer(
        compute="_compute_time_delay",
        readonly=True,
    )
    is_time_exceeded = fields.Boolean(
        compute="_compute_is_time_exceeded",
        search="_search_is_time_exceeded",
    )

    @api.depends("grn_date")
    def _compute_time_delay(self):
        today = datetime.today().strftime("%Y-%m-%d")
        for rec in self:
            if rec.grn_date:
                time = rec.grn_date.strftime("%Y-%m-%d")
                rec.time_delay = numpy.busday_count(time, today)
            else:
                rec.time_delay = 0

    @api.depends("time_delay")
    def _compute_is_time_exceeded(self):
        max_time = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_grn.max_delay_to_process_receipt")
        )
        for rec in self:
            rec.is_time_exceeded = rec.time_delay >= max_time

    def _search_is_time_exceeded(self, operator, value):
        max_time = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_grn.max_delay_to_process_receipt")
        )
        search_time_exceeded = (
            # is_time_exceeded != False
            (operator in NEGATIVE_TERM_OPERATORS and not value)
            or
            # is_time_exceeded = True
            (operator not in NEGATIVE_TERM_OPERATORS and value)
        )

        min_date = datetime.now() - timedelta(days=max_time)
        if search_time_exceeded:
            return [("grn_date", "<=", min_date)]
        return ["|", ("grn_date", "=", False), ("grn_date", ">", min_date)]
