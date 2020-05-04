# -*- coding: utf-8 -*-
# Copyright 2019 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _generate_moves(self):
        """ When an inventory is validated, we need to cancel any remaining
        pending inventory moves """
        loss_picking_type = self.env.ref("stock_lot_loss.stock_picking_type_23")
        moves = self.env["stock.move"]
        for line in self:
            search_domain = [
                ("qty", ">", 0.0),
                ("product_id", "=", line.product_id.id),
                ("package_id", "=", line.package_id.id),
                ("location_id", "=", line.location_id.id),
                (
                    "reservation_id.picking_id.picking_type_id",
                    "=",
                    loss_picking_type.id,
                ),
            ]
            if line.prod_lot_id:
                search_domain.append(("lot_id", "=", line.prod_lot_id.id))
            quants = self.env["stock.quant"].search(search_domain)
            moves |= quants.mapped("reservation_id")
        if moves:
            moves.action_cancel()
        return super(StockInventoryLine, self)._generate_moves()
