# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    number_of_parcels_idx = fields.Integer(
        string="Number of Parcels Index",
        help="The index of the current package in the list of parcels "
        "for the delivery package type.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Override to set the package name that could have been set in the
        # context.
        for vals in vals_list:
            if "name" not in vals and "default_package_name" in self.env.context:
                vals["name"] = self.env.context["default_package_name"]
            if (
                "number_of_parcels_idx" not in vals
                and "default_number_of_parcels_idx" in self.env.context
            ):
                vals["number_of_parcels_idx"] = self.env.context[
                    "default_number_of_parcels_idx"
                ]
        return super().create(vals_list)
