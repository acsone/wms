# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import first

from odoo.addons.stock.models.stock_move import StockMove as Move


class StockMove(Move):
    def _merge_moves_fields(self) -> dict:
        """
        If the move is linked to a location orderpoint, get the max of priority.

        as the new priority.
        As the moves are merged, get the orderpoint for the max quantity
        to stay on the merged move.
        """
        res = super()._merge_moves_fields()
        if any(move.location_orderpoint_id for move in self):
            priority = max(move.priority for move in self)
            orderpoint = first(
                self.filtered(
                    lambda move: move.priority == priority
                ).location_orderpoint_id
            )
            res.update(
                {
                    "priority": max(move.priority for move in self),
                }
            )
            if orderpoint:
                res.update(
                    {
                        "location_orderpoint_id": orderpoint.id,
                    }
                )
        return res

    def _inverse_priority(self):
        """
        This is mandatory to override as "stock_move_manage_priority" module.

        prevents to modify the priority under some conditions.

        Here, in the case the location orderpoint is filled in, allow
        to write the priority (coming for procurement run).
        """
        orderpoint_moves = self.filtered("location_orderpoint_id")
        return super(StockMove, (self - orderpoint_moves))._inverse_priority()
