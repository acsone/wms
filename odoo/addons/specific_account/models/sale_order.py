# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    date_order_short = fields.Date(compute="_compute_date_order_short")

    @api.depends("date_order")
    def _compute_date_order_short(self):
        for sale in self:
            if sale.date_order:
                sale.date_order_short = datetime.strptime(
                    sale.date_order, DEFAULT_SERVER_DATETIME_FORMAT
                ).date()
