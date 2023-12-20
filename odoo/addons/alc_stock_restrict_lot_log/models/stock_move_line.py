# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import traceback

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase

_logger = logging.getLogger("restrict-lot-error")


class StockMoveLine(StockMoveLineBase):
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if (
                rec.lot_id
                and rec.move_id.restrict_lot_id
                and rec.lot_id != rec.move_id.restrict_lot_id
            ):
                _logger.error("\n".join(traceback.format_stack()))
        return res
