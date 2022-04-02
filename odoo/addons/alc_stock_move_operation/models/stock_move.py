# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    pack_operation_ids = fields.One2many(
        comodel_name="stock.pack.operation",
        compute="_compute_pack_operation_ids",
        help="Pack operations linked to the move",
    )

    @api.depends("linked_move_operation_ids", "linked_move_operation_ids.move_id")
    def _compute_pack_operation_ids(self):
        for rec in self:
            rec.pack_operation_ids = rec.linked_move_operation_ids.mapped(
                "operation_id"
            )
