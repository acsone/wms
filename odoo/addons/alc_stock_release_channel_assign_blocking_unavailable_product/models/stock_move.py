# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):

    delivery_requires_other_lines = fields.Boolean(readonly=True)
    product_qty_unavailable = fields.Float()

    def _get_stock_release_channel_block_on_backorder(self):
        """Get the condition to block further delivery on backorder."""
        self.ensure_one()
        return bool(self.product_qty_unavailable > 0)
