# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import index_exists

from odoo.addons.stock.models.stock_lot import StockLot as LotBase


class StockLot(LotBase):
    def init(self):  # pylint: disable=missing-return
        """This index improves the overall performance of picking validation."""
        super().init()
        if not index_exists(self._cr, "stock_lot_expiration_date_manidx"):
            self._cr.execute(
                """
                CREATE INDEX stock_lot_expiration_date_manidx
                ON
                    stock_lot(expiration_date)
                """
            )
