# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def create(self, vals):
        """Disable check in src/addons/stock/models/stock_production_lot.py"""
        if self.env.context.get("active_pack_operation", False):
            self = self.with_context(active_pack_operation=False)
        return super(StockProductionLot, self).create(vals)
