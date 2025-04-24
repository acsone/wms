# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    delivery_requires_other_lines = fields.Boolean(readonly=True)
    product_qty_unavailable = fields.Float()
    delivery_requires_other_lines_label = fields.Char(
        compute="_compute_delivery_requires_other_lines_label",
    )

    @api.depends("delivery_requires_other_lines")
    def _compute_delivery_requires_other_lines_label(self):
        """Compute the label for delivery requires other lines."""
        for move in self:
            if move.delivery_requires_other_lines:
                move.delivery_requires_other_lines_label = _(
                    "Delivery Requires Other Lines"
                )
            else:
                move.delivery_requires_other_lines_label = ""

    def _get_stock_release_channel_block_on_backorder(self):
        """Get the condition to block further delivery on backorder."""
        self.ensure_one()
        return bool(self.product_qty_unavailable > 0)
