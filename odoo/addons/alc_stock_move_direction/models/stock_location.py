# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_helper.models.stock_location import (
    StockLocation as StockLocationBase,
)


class StockLocation(StockLocationBase):
    def write(self, vals):
        warehouse_model = self.env["stock.warehouse"]
        if (
            set(self.ids).intersection(
                warehouse_model._get_stock_locations_boundaries().keys()
            )
            and "location_id" in vals
        ):
            warehouse_model._clear_stock_locations_boundaries_cache()
        return super().write(vals)
