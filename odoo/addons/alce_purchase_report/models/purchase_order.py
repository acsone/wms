# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    last_date_done = fields.Datetime(
        string="Last date of Transfer", compute="_compute_last_date_done", store=True
    )

    @api.depends("order_line.qty_received")
    def _compute_last_date_done(self):
        for order in self:
            if order.is_shipped:
                order.last_date_done = max(order.picking_ids.mapped("date_done"))
            else:
                order.last_date_done = False
