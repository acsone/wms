# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockLocation(models.Model):

    _inherit = "stock.location"

    def write(self, vals):
        ids = self.ids
        Warehouse = self.env["stock.warehouse"]
        if set(ids).intersection(Warehouse._get_stock_locations_boundaries().keys()):
            Warehouse._clear_stock_locations_boundaries_cache()
        return super(StockLocation, self).write(vals)
