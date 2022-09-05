# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def _create_backorder(self):
        self._prevent_new_delivery_if_only_backorders()
        return super(StockPicking, self)._create_backorder()

    def _prevent_new_delivery_if_only_backorders(self):
        """When a backorder is created for picking out we set the
        'delivery_requires_other_lines' flag on the move lines remaining to
        deliver. In this way we prevent the delivery of these lines if no new
        SO has been made after the current delivery to avoid making a delivery
        free of charge
        """
        outgoing_pickings = self.filtered(lambda p: p.picking_type_code == "outgoing")
        if not outgoing_pickings:
            return
        moves_not_delivered = outgoing_pickings.mapped("move_lines").filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        moves_not_delivered |= moves_not_delivered.mapped("move_orig_ids")
        moves_not_delivered_to_write = moves_not_delivered.filtered(
            lambda p: not p.delivery_requires_other_lines
        )
        moves_not_delivered_to_write.write({"delivery_requires_other_lines": True})
