# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def _create_backorder(self):
        backorders = super()._create_backorder()
        if self.env.company.no_user_on_backorder:
            backorders.write({"user_id": False})
        return backorders
