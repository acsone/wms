# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):
    net_weight = fields.Float(compute="_compute_weight_without_depends")
    forecast_weight = fields.Float(compute="_compute_weight_without_depends")

    # AFAIK, there is no way to remove a field for @api.depends as it's by design
    # cumulative and merge all fields across inheritance.
    # there is no other solution but to redefine the compute method without the
    # decorator
    # I double-checked, these fields are used only in view and have no functional usage
    def _compute_weight_without_depends(self):
        self._compute_weight()
