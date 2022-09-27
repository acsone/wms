# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _get_out_picking(self):
        # bypass the super entirely, this is coupled so sale.order _compute_picking_ids
        domain = [
            ("group_id", "in", self.move_lines.mapped("group_id").ids),
            ("picking_type_id.code", "=", "outgoing"),
            ("picking_id.state", "not in", ["cancel", "done"]),
        ]
        move = self.env["stock.move"].search(domain, limit=1)
        return move.picking_id
