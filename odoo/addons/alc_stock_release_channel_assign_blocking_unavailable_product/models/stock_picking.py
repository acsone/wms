# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_release_channel.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):

    delivery_requires_other_lines = fields.Boolean(
        compute="_compute_delivery_requires_other_lines"
    )
    ignore_release_channel_block = fields.Boolean(default=False)

    @api.depends("move_ids", "move_ids.delivery_requires_other_lines")
    def _compute_delivery_requires_other_lines(self):
        for rec in self:
            rec.delivery_requires_other_lines = bool(rec.move_ids) and all(
                m.delivery_requires_other_lines for m in rec.move_ids
            )

    def _create_backorder(self):
        backorders = super()._create_backorder()
        for move in backorders.move_ids:
            move.delivery_requires_other_lines = move.product_qty_unavailable > 0
        return backorders

    def button_ignore_release_channel_block(self):
        self.write({"ignore_release_channel_block": True})
        self.assign_release_channel()
        return True
