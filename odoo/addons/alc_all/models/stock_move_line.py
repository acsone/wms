# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import index_exists

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):
    """Create this index manually to improve performances on computing shipping_weight field."""

    def init(self):  # pylint: disable=missing-return
        super().init()
        if not index_exists(
            self._cr,
            "stock_move_line_result_package_id_manidx",
        ):
            self._cr.execute(
                """
                create index concurrently stock_move_line_result_package_id_manidx ON stock_move_line(result_package_id);
                """
            )
