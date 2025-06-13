# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_stock_picking_parcels_and_items_per_source.models.stock_picking import (
    StockPicking as Picking,
)


class StockPicking(Picking):
    rma_id = fields.Many2one(
        comodel_name="rma",
        compute="_compute_rma_id",
        store=False,
        search="_search_rma_id",
    )

    @api.depends("origin")
    def _compute_rma_id(self):
        for picking in self:
            picking.rma_id = self.env["rma"].search(
                [("name", "=", picking.origin)], limit=1
            )

    def _search_rma_id(self, operator, value):
        if operator == "=":
            return [("origin", "=", self.env["rma"].browse(value).name)]
        if operator == "!=":
            return [("origin", "!=", self.env["rma"].browse(value).name)]
        return []
