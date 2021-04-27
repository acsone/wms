# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.multi
    def _create_picking(self):
        result = super(PurchaseOrder, self)._create_picking()
        StockPicking = self.env["stock.picking"]
        route_froid_frigo = self.env.ref(
            "__setup__.stock_location_route_pick_froid", raise_if_not_found=False
        )
        move_lines_froid_frigo = None
        for order in self:
            origin_pickings = order.picking_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )
            if route_froid_frigo:
                move_lines_froid_frigo = origin_pickings.mapped("move_lines").filtered(
                    lambda m: route_froid_frigo in m.product_id.route_ids
                )

            if move_lines_froid_frigo:
                pickings_frigo = order.picking_ids.filtered(
                    lambda x: x.state not in ("done", "cancel") and x.is_picking_frigo
                )
                if not pickings_frigo:

                    res = order._prepare_picking()
                    picking_frigo = StockPicking.create(res)
                    picking_frigo.write({"is_picking_frigo": True})

                else:
                    picking_frigo = pickings_frigo[0]

                for move_line in move_lines_froid_frigo:
                    move_line.picking_id = picking_frigo.id
                move_lines_froid_frigo.force_assign()
                origin_pickings.mapped("move_lines").force_assign()
        return result
