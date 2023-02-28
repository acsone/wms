# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.stock_picking_batch.models.stock_picking_batch import (
    StockPickingBatch as StockPickingBatchBase,
)


class StockPickingBatch(StockPickingBatchBase):

    # Odoo Fix: never copy the printed field. Important for backorder creation
    printed = fields.Boolean(compute="_compute_printed", inverse="_inverse_printed")

    operator_id = fields.Many2one(
        "res.users",
        string="Operator",
        copy=False,
        tracking=True,
        inverse="_inverse_operator_id",
    )

    _sql_constraints = [
        (
            "operator_id_unique",
            "EXCLUDE (operator_id WITH =) WHERE ( operator_id is not null and state not in ('done', 'cancel', 'released'))",
            _("This operator is already assigned to a wave"),
        )
    ]

    def _prepare_assign_operator_values(self, operator=None):
        operator_id = operator.id if operator else self.env.uid
        return {"operator_id": operator_id, "printed": True}

    def assign_operator(self, operator=None):
        self.write(self._prepare_assign_operator_values(operator))

    def _inverse_operator_id(self):
        for rec in self:
            rec.user_id = rec.operator_id
            rec.picking_ids.write({"user_id": rec.operator_id.id})

    @api.depends("picking_ids", "picking_ids.printed")
    def _compute_printed(self):
        for rec in self:
            rec.printed = all(rec.picking_ids.mapped("printed"))

    def _inverse_printed(self):
        for rec in self:
            rec.picking_ids.write({"printed": rec.printed})
