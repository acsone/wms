# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_release_channel_user.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _should_check_user(self):
        self.ensure_one()
        is_gls = self.delivery_type == "gls"
        skip_gls = is_gls and self.picking_type_id.code == "outgoing"
        return not skip_gls and super()._should_check_user()
