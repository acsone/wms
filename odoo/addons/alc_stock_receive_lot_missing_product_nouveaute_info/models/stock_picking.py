# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"
    has_missing_info = fields.Boolean(
        default=False, compute="_compute_has_missing_info"
    )

    @api.depends("pack_operation_ids")
    def _compute_has_missing_info(self):
        for rec in self:
            packops = rec.mapped("pack_operation_ids")
            rec.has_missing_info = any(packops.mapped("has_missing_info"))
