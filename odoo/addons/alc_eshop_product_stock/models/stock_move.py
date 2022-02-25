# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_product_to_update(self):
        # This method return the list of product we will recompute the
        # stock for the eshop. Filter out internal moves before calling super
        # to only take into account product from incoming and outgoing
        # moves
        moves = self.filtered(
            lambda m: m.is_outgoing_move() or m.is_incoming_move() or m.is_scrap()
        )
        return super(StockMove, moves)._get_product_to_update()

    def is_outgoing_move(self):
        self.ensure_one()
        if (
            self.picking_type_id.code in (False, "outgoing")
            and (
                self.location_id.usage == "internal"
                and self.location_dest_id.usage == "customer"
            )
            or (
                self.location_id.usage == "internal"
                and self.location_dest_id.usage == "inventory"
            )
            or (
                self.location_id.usage == "internal"
                and self.location_dest_id.usage == "supplier"
            )
        ):
            return True
        return False

    def is_scrap(self):
        self.ensure_one()
        return self.location_id.scrap_location or self.location_dest_id.scrap_location

    def is_incoming_move(self):
        self.ensure_one()
        if (
            self.picking_type_id.code in (False, "incoming")
            and (
                self.location_id.usage == "supplier"
                and self.location_dest_id.usage == "internal"
            )
            or (
                self.location_id.usage == "inventory"
                and self.location_dest_id.usage == "internal"
            )
            or (
                self.location_id.usage == "customer"
                and self.location_dest_id.usage == "internal"
            )
        ):
            return True
        return False
