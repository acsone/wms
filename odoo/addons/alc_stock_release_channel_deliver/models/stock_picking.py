# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.osv.expression import AND

from odoo.addons.stock_release_channel.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _get_release_channel_possible_candidate_domain(self):
        self.ensure_one()
        domain = [("state", "not in", ("delivering", "delivering_error", "delivered"))]
        return AND([super()._get_release_channel_possible_candidate_domain(), domain])
