# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine_product_stock.models.stock_move import (
    StockMove as StockMoveBase,
)


class StockMove(StockMoveBase):
    def _get_product_to_update(self):
        # This method return the list of product we will recompute the
        # stock for the eshop. Filter out internal moves before calling super
        # to only take into account product from incoming and outgoing
        # moves
        moves = self.filtered(
            lambda m: m.is_inventory
            or m._is_outgoing()
            or m._is_incoming()
            or m._is_stock_replenishment()
            or m._is_scrap()
        )
        return super(StockMove, moves)._get_product_to_update()

    def _is_scrap(self):
        self.ensure_one()
        return self.location_id.scrap_location or self.location_dest_id.scrap_location
