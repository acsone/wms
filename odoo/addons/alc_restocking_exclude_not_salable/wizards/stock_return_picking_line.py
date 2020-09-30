# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReturnPickingLine(models.TransientModel):

    _inherit = "stock.return.picking.line"

    not_salable_product = fields.Boolean(
        readonly=True, default=False, compute="_compute_not_salable_product"
    )

    @api.depends("product_id")
    def _compute_not_salable_product(self):
        for rec in self:
            rec.not_salable_product = not rec.product_id.sale_ok
