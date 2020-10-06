# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp S.A.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        result = super(StockMove, self).action_done()
        for move in self.filtered("origin_returned_move_id"):
            line = move.procurement_id.sale_line_id
            if not move._include_move_into_return_quantity():
                continue
            if move.location_dest_id.usage != "customer":
                line.product_qty_returned += move.product_uom_qty
            else:
                line.product_qty_returned -= move.product_uom_qty
        return result

    @api.multi
    def _include_move_into_return_quantity(self):
        self.ensure_one()
        line = self.procurement_id.sale_line_id
        if self.product_id.expense_policy != "no" or not line:
            return False
        return True
