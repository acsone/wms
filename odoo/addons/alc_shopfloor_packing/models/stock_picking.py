# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    is_shopfloor_packing_todo = fields.Boolean(
        "Operations need to be packed",
        help="If set, some operations need to be packed by the shopdloor operator",
        compute="_compute_is_shopfloor_packing_todo",
    )

    @api.depends("pack_operation_ids", "pack_operation_ids.result_package_id")
    def _compute_is_shopfloor_packing_todo(self):
        for rec in self:
            rec.is_shopfloor_packing_todo = False
            for packop in rec.pack_operation_ids:
                if packop.result_package_id and packop.result_package_id.is_internal:
                    rec.is_shopfloor_packing_todo = True
                    break
