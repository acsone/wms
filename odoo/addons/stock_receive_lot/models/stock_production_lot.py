# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def create(self, vals):
        """Disable check in src/addons/stock/models/stock_production_lot.py"""
        new_self = self
        if self.env.context.get("active_pack_operation", False):
            new_self = self.with_context(active_pack_operation=False)
        return super(StockProductionLot, new_self).create(vals)
