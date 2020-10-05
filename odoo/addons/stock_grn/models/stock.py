# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright (C) 2015-TODAY BCIM <http://www.bcim.be>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS


class StockPicking(models.Model):
    _inherit = "stock.picking"

    grn_id = fields.Many2one(
        comodel_name="stock.grn",
        string="Goods Received Note",
        copy=False,
        readonly=True,
    )
    grn_date = fields.Datetime(
        related="grn_id.date", string="GRN Date", store=True, index=True, readonly=True
    )
    time_delay = fields.Integer(compute="_compute_time_delay", readonly=True, default=0)
    is_time_exceeded = fields.Boolean(
        default=False,
        compute="_compute_is_time_exceeded",
        search="_search_is_time_exceeded",
    )

    @api.depends("grn_date")
    def _compute_time_delay(self):
        for rec in self:
            if rec.grn_date:
                time_delta = datetime.today() - datetime.strptime(
                    rec.grn_date, "%Y-%m-%d %H:%M:%S"
                )
                rec.time_delay = time_delta.days

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


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    @api.multi
    def _get_action(self, action_xmlid):
        result = super(StockPickingType, self)._get_action(action_xmlid)
        if self:
            if self.code == "incoming":
                result["context"] = result["context"].replace(
                    "{", "{'search_default_grn':1,", 1
                )
        return result
