# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_release_channel.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):

    is_backorder_due_to_unavailability = fields.Boolean(
        compute="_compute_is_backorder_due_to_unavailability"
    )
    ignore_release_channel_block = fields.Boolean(default=False)

    @api.depends("move_ids", "move_ids.is_backorder")
    def _compute_is_backorder_due_to_unavailability(self):
        for rec in self:
            rec.is_backorder_due_to_unavailability = bool(rec.move_ids) and all(
                m.is_backorder and m.product_qty_unavailable > 0 for m in rec.move_ids
            )

    def _create_backorder(self):
        backorders = super()._create_backorder()
        backorders.move_ids.write({"is_backorder": True})
        return backorders

    def button_ignore_release_channel_block(self):
        self.write({"ignore_release_channel_block": True})
        self.assign_release_channel()
        return True
