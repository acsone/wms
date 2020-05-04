# -*- coding: utf-8 -*-
# © 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def get_price_unit(self):
        # we reimplement get_price_unit to force getting the price of the
        # purchase line from the PO line when the move gets done, because
        # Alcyon can change the price of the line *after* the RFQ is confirmed
        # to a PO (and the stock.move is generated with the original price),
        # which breaks the average price computation of the products).
        price_unit = super(StockMove, self).get_price_unit()
        if self.purchase_line_id:  # this is called already in a loop on self
            price_unit = self.purchase_line_id._get_stock_move_price_unit()
            self.write({"price_unit": price_unit})
        return price_unit
