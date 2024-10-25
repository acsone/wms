# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import drop_index, index_exists

from odoo.addons.stock_account.models import stock_valuation_layer


class StockValuationLayer(stock_valuation_layer.StockValuationLayer):

    def init(self):  # pylint: disable=missing-return
        super().init()

        if index_exists(
            self._cr,
            "stock_valuation_layer_index",
        ):
            # covered by the previous index
            drop_index(
                self._cr,
                "stock_valuation_layer_product_id_manidx",
                "stock_valuation_layer",
            )
