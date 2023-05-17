# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock.models.stock_picking import Picking as PickingBase


class StockPicking(PickingBase):

    _inherit = "stock.picking"
    has_missing_info = fields.Boolean(
        default=False, compute="_compute_has_missing_info"
    )

    @api.depends("move_line_ids")
    def _compute_has_missing_info(self):
        for rec in self:
            move_lines = rec.mapped("move_line_ids")
            rec.has_missing_info = any(move_lines.mapped("has_missing_info"))
