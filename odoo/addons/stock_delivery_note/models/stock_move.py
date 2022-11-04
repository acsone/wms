# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

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

    suite_name = fields.Char(compute="_compute_suite_name")

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

    def _compute_suite_name(self):
        for move in self:
            move.suite_name = move._get_suite_name()

    def _get_suite_name(self, sale_order=None, delivery_date=None):
        """ Compute last column of the delivery note.

        Don't know what it is called but it is also found on the
        deliverslip report.
        """
        self.ensure_one()
        if not sale_order:
            sale_order = self.order_line_id.order_id
        if not delivery_date:
            delivery_date = self.picking_id.date_done or self.picking_id.date
        customer = sale_order.partner_id
        depot_number = customer.vet_depot_number or customer.parent_id.vet_depot_number
        if not depot_number:
            return sale_order.client_order_ref or ""
        return "/".join(
            [
                datetime.strptime(delivery_date, "%Y-%m-%d %H:%M:%S").strftime("%y"),
                depot_number,
                sale_order.suite_name or "0000",
            ]
        )
