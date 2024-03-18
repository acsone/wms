# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_move import StockMove as StockMoveBase


class StockMove(StockMoveBase):
    def _get_dest_locations(self):
        """Get the destination locations.

        If the move has some operation, the locations to consider are
        the locations on the operations, otherwise we take the one on
        the move.
        """
        self.ensure_one()
        destinations = self.location_dest_id
        if self.state in ("partially_available", "assigned", "done"):
            destinations = self.mapped("move_line_ids.location_dest_id")
        return destinations or self.location_dest_id

    def _is_outgoing(self):
        self.ensure_one()
        origin_stock_location = self.env["stock.warehouse"]._get_stock_location(
            self.location_id
        )
        if not origin_stock_location:
            # we are not in a stock location ...
            return False
        for dest_location in self._get_dest_locations():
            dest_stock_location = self.env["stock.warehouse"]._get_stock_location(
                dest_location
            )
            if (
                origin_stock_location
                and dest_stock_location
                and origin_stock_location != dest_stock_location
            ):
                return True

            if not dest_location.is_sublocation_of(origin_stock_location):
                return True
        return False

    def _is_incoming(self):
        self.ensure_one()
        origin_stock_location = self.env["stock.warehouse"]._get_stock_location(
            self.location_id
        )
        for dest_location in self._get_dest_locations():
            dest_stock_location = self.env["stock.warehouse"]._get_stock_location(
                dest_location
            )
            if (
                origin_stock_location
                and dest_stock_location
                and origin_stock_location != dest_stock_location
            ):
                return True
            if not origin_stock_location and dest_stock_location:
                return True
        return False

    def _is_stock_replenishment(self) -> bool:
        """
        In some configuration of stock locations, we maybe want to know.

        if the move goes into stock (e.g.: We have a parking location that
        is not considered as real Stock)
        """
        self.ensure_one()
        for dest_location in self._get_dest_locations():
            if dest_location.filtered_domain(
                [("id", "child_of", dest_location.warehouse_id.lot_stock_id.id)]
            ):
                return True
        return False
