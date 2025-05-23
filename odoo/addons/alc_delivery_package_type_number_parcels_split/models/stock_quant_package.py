# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    @api.model_create_multi
    def create(self, vals_list):
        # Override to set the package name that could have been set in the
        # context.
        for vals in vals_list:
            if "name" not in vals and "default_package_name" in self.env.context:
                vals["name"] = self.env.context["default_package_name"]
        return super().create(vals_list)
