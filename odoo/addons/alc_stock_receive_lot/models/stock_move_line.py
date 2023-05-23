# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):
    @api.depends("product_id", "reserved_uom_qty", "qty_done")
    def name_get(self):
        result = []
        for line in self:
            reference = line.product_id.default_code
            product_name = line.product_id.name
            qty = line.reserved_uom_qty
            qty_done = line.qty_done
            name = f"[{reference}] {product_name} ({qty_done} / {qty})"
            result.append((line.id, name))
        return result
