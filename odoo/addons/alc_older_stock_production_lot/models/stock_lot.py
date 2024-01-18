# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.stock.models import stock_lot


class StockLot(stock_lot.StockLot):
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.filtered("expiration_date").product_id.invalidate_recordset(
            ["older_lot_id", "best_before_date"]
        )
        return res

    def write(self, vals):
        res = super().write(vals)
        if "expiration_date" in vals:
            self.product_id.invalidate_recordset(["older_lot_id", "best_before_date"])
        return res
