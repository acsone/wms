# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    date_announced = fields.Datetime(string="Announced Date", index=True, copy=False)
    is_modify_date_announced_allowed = fields.Boolean(
        "Can modify date announced",
        compute="_compute_is_modify_date_announced_allowed",
        default=True,
        readonly=True,
        store=True,
    )

    @api.multi
    @api.depends("move_ids", "move_ids.state")
    def _compute_is_modify_date_announced_allowed(self):
        """
        Compute if the the date announced can still be modified or not
        :return:
        """
        for line in self:
            line.is_modify_date_announced_allowed = (
                len(line.move_ids.filtered(lambda m: m.state not in ("cancel", "done")))
                > 0
            )
