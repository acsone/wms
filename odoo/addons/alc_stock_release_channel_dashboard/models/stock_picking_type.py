# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.tools import ormcache

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):
    @api.model
    @ormcache()
    def _get_ids_visible_in_dashboard(self):
        return self.search([("release_channel_can_allow_pick", "=", True)]).ids

    @api.model
    def _get_visible_in_dashboard(self):
        return self.browse(self._get_ids_visible_in_dashboard())

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._get_ids_visible_in_dashboard.clear_cache(self)
        return res

    def write(self, vals):
        res = super().write(vals)
        self._get_ids_visible_in_dashboard.clear_cache(self)
        return res
