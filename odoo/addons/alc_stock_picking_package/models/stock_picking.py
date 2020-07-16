# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    stock_quant_package_ids = fields.One2many(
        comodel_name="stock.quant.package",
        string="Package ids",
        compute="_compute_stock_quant_package_ids",
    )

    @api.multi
    @api.depends("pack_operation_pack_ids", "pack_operation_pack_ids.package_id")
    def _compute_stock_quant_package_ids(self):
        for record in self:
            record.stock_quant_package_ids = record.mapped(
                "pack_operation_pack_ids.package_id"
            )
