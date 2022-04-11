# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, tools


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    @api.model
    @tools.ormcache()
    def _get_stock_locations_boundaries(self):
        """return a dict by stock location of parent_left, parent_right."""
        warehouses = self.search([])
        return {
            wh.lot_stock_id.id: (
                wh.lot_stock_id.parent_left,
                wh.lot_stock_id.parent_right,
            )
            for wh in warehouses
        }

    def _get_stock_location(self, location):
        """Get the stock location for the given location."""
        location_id = None
        for (
            lid,
            (parent_left, parent_right),
        ) in self._get_stock_locations_boundaries().items():
            if (
                parent_left <= location.parent_left
                and parent_right >= location.parent_right
            ):
                location_id = lid
                break
        StockLocation = self.env["stock.location"]
        if location_id:
            return StockLocation.browse(location_id)
        return StockLocation.browse()

    @api.model
    def create(self, vals):
        self._clear_stock_locations_boundaries_cache()
        return super(StockWarehouse, self).create(vals)

    def write(self, vals):
        if "lot_stock_id" in vals:
            self._clear_stock_locations_boundaries_cache()
        return super(StockWarehouse, self).write(vals)

    def _clear_stock_locations_boundaries_cache(self):
        self._get_stock_locations_boundaries.clear_cache(self)
