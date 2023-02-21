# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.sale_stock_restocking_fee_invoicing.models import stock_move


class StockMove(stock_move.StockMove):
    def _is_restocking_fee_chargeable(self):
        self.ensure_one()
        if self.is_additional_move:
            return False  # not sure it can be reached anymore !
        return super()._is_restocking_fee_chargeable()
