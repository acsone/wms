# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_receive_lot.models.stock_picking import Picking


class StockPicking(Picking):
    def button_receive(self):
        self.filtered(lambda r: not r.started).action_start()
        return super().button_receive()
