# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, tools

from odoo.addons.stock.models.stock_warehouse import Warehouse


class StockWarehouse(Warehouse):
    @api.model
    @tools.ormcache()
    def _get_stock_locations_boundaries(self):
        """Return a dict by stock location parent."""
        warehouses = self.search([])
        return {
            wh.view_location_id.id: wh.view_location_id.parent_path for wh in warehouses
        }

    def _get_stock_location(self, location):
        """Get the stock location for the given location."""
        stock_location_model = self.env["stock.location"]
        for (
            lot_stock_id,
            parent_path,
        ) in self._get_stock_locations_boundaries().items():
            if location.parent_path.startswith(parent_path):
                return stock_location_model.browse(lot_stock_id)
        return self.env["stock.location"].browse()

    @api.model_create_multi
    def create(self, vals_list):
        self._clear_stock_locations_boundaries_cache()
        return super().create(vals_list)

    def write(self, vals):
        if "lot_stock_id" in vals:
            self._clear_stock_locations_boundaries_cache()
        return super().write(vals)

    def _clear_stock_locations_boundaries_cache(self):
        self._get_stock_locations_boundaries.clear_cache(self)
