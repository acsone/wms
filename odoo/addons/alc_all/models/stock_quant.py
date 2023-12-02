# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import index_exists

from odoo.addons.stock.models.stock_quant import StockQuant as StockQuantBase


class StockQuant(StockQuantBase):
    def init(self):  # pylint: disable=missing-return
        """
        This index improves the overall performance of picking validation.

        A flush_all in _update_reserved_quantity makes the computed fields recomputed
        with each stock.move action_done.
        """
        super().init()
        if not index_exists(self._cr, "stock_quant_location_id_product_id_manidx"):
            self._cr.execute(
                """
                CREATE INDEX stock_quant_location_id_product_id_manidx
                ON
                    stock_quant (location_id, product_id)
                """
            )
