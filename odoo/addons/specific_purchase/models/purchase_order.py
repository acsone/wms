# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import date, timedelta

import pytz

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    total_weight = fields.Float(
        "Total weight",
        compute="_compute_total_weight",
        readonly=True,
        help="Total weight in Kg",
    )

    @api.model
    def convert_time(self, pl_day, pl_time=14.00):
        """
        mock float field to respect user timezone
        pl_day - date in string format
        pl_time - time in float format
        """
        tz_utc = pytz.timezone("UTC")
        tz_context = pytz.timezone(self.env.context.get("tz", "UTC"))

        new_planned_date = fields.Datetime.from_string(pl_day)
        hour = int(pl_time)
        minute = int(round(pl_time - hour) * 60)
        new_planned_date = new_planned_date.replace(hour=hour, minute=minute, second=0)
        return tz_context.localize(new_planned_date).astimezone(tz_utc)

    @api.multi
    def _compute_total_weight(self):
        for po in self:
            total_weight = 0
            for line in po.order_line:
                total_weight += line.product_id.weight * line.product_qty

            po.total_weight = total_weight
