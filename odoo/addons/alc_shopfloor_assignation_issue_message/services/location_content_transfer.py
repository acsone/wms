# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class LocationContentTransfer(Component):
    _inherit = "shopfloor.location.content.transfer"

    def _check_moves_assignation(self, new_moves):
        res = super(LocationContentTransfer, self)._check_moves_assignation(new_moves)
        unassigned_moves = new_moves.filtered(lambda m: m.state != "assigned")
        blocking_pickings = self.env["stock.picking"]
        if unassigned_moves:
            location = unassigned_moves.mapped("location_id")
            products = unassigned_moves.mapped("product_id")
            product_templates = products.mapped("product_tmpl_id")
            quants = self.env["stock.quant"].search(
                [("product_id", "in", products.ids), ("location_id", "=", location.id)]
            )
            reserved_moves = quants.mapped("reservation_id")
            blocking_pickings = reserved_moves.mapped("picking_id")

        if blocking_pickings:
            return self.msg_store.reserved_moves_in_current_location(
                location, product_templates.mapped("name"), blocking_pickings
            )

        return res
