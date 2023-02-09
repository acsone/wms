# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_additional_product_stock.models.stock_move import (
    StockMove as StockMoveBase,
)


class StockMove(StockMoveBase):
    def _include_move_into_return_quantity(self):
        self.ensure_one()
        if self.is_additional_move:
            return False

        return super()._include_move_into_return_quantity()
