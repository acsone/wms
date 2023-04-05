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
    nbr_lines = fields.Integer("Nbr lines", compute="_compute_nbr_lines", readonly=True)
    nbr_lines_bo = fields.Integer(
        "Nbr lines BO",
        compute="_compute_nbr_lines_bo",
        search="_search_nbr_lines_bo",
        readonly=True,
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
    def _compute_nbr_lines(self):
        """
        Compute the number of lines by purchase order.
        :return:
        """
        for po in self:
            po.nbr_lines = len(po.order_line)

    @api.multi
    def _compute_nbr_lines_bo(self):
        """
        Compute the number of lines with back order by purchase order.
        :return:
        """
        for po in self:
            # NOTE: computing 'immediately_usable_qty' field is very slow,
            # especially when the field is displayed on PO tree view
            po.nbr_lines_bo = len(
                po.order_line.filtered(
                    lambda line: line.product_id.immediately_usable_qty < 0
                )
            )

    def _search_nbr_lines_bo(self, operator, value):
        orders = self.browse()
        draft_orders = self.search([("state", "=", "draft")])
        for order in draft_orders:
            # NOTE: actual operator is ignored here for the sake of simplicity.
            # To implement if it's really needed.
            if order.nbr_lines_bo:
                orders |= order
        return [("id", "in", orders.ids)]

    @api.multi
    def _compute_total_weight(self):
        for po in self:
            total_weight = 0
            for line in po.order_line:
                total_weight += line.product_id.weight * line.product_qty

            po.total_weight = total_weight

    @api.multi
    def button_confirm(self):
        self.responsible_id = self.env.user.id

        return super(PurchaseOrder, self).button_confirm()
