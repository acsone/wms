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

    @api.multi
    def _compute_total_weight(self):
        for po in self:
            total_weight = 0
            for line in po.order_line:
                total_weight += line.product_id.weight * line.product_qty

            po.total_weight = total_weight
