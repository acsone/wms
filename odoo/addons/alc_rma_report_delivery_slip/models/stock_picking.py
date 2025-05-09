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
    rma_reason = fields.Char(compute="_compute_rma_reason", store=False)
    rma_operation = fields.Char(compute="_compute_rma_operation", store=False)

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

    @api.depends("origin", "rma_id.reason_id")
    def _compute_rma_reason(self):
        for picking in self:
            picking.rma_reason = self.rma_id.reason_id.name

    @api.depends("origin", "rma_id.operation_id")
    def _compute_rma_operation(self):
        for picking in self:
            picking.rma_operation = self.rma_id.operation_id.name
