# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.stock_picking_batch.models.stock_picking_batch import (
    StockPickingBatch as StockPickingBatchBase,
)


class StockPickingBatch(StockPickingBatchBase):

    # Odoo Fix: never copy the printed field. Important for backorder creation
    printed = fields.Boolean(compute="_compute_printed", inverse="_inverse_printed")

    _sql_constraints = [
        (
            "user_id_unique",
            "EXCLUDE (user_id WITH =) WHERE ( user_id is not null and state not in ('done', 'cancel', 'released'))",
            _("This operator is already assigned to a wave"),
        )
    ]

    @api.depends("picking_ids", "picking_ids.printed")
    def _compute_printed(self):
        for rec in self:
            rec.printed = all(rec.picking_ids.mapped("printed"))

    def _inverse_printed(self):
        for rec in self:
            rec.picking_ids.write({"printed": rec.printed})
