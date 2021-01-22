# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    order_line_id = fields.Many2one(
        "sale.order.line",
        string="Order line",
        related="procurement_id.sale_line_id",
        store=True,
        readonly=True,
    )

    order_id = fields.Many2one("sale.order", related="order_line_id.order_id")

    @api.multi
    def get_lots(self, only_with_lot=True):
        """
        Return all lots for the stock move
        :param only_with_lot: filter quants without lot

        :return: Return a list of tuple
        """
        qty_by_lot = {}
        quants = self.quant_ids
        for quant in quants:
            if not quant.lot_id:
                if only_with_lot:
                    continue
                qty_by_lot[None] = [qty_by_lot.get(None, [0])[0] + quant.qty, ""]
                continue
            lot = quant.lot_id

            existing_qty = qty_by_lot.get(lot.name, [])
            if existing_qty:
                qty_by_lot[lot.name] = [existing_qty[0] + quant.qty, existing_qty[1]]
            else:
                qty_by_lot[lot.name] = [quant.qty, lot.life_date or ""]

        result = [[key, value[0], value[1]] for key, value in qty_by_lot.iteritems()]

        # Sort lot by name
        return sorted(result, key=lambda lot: lot[0])
