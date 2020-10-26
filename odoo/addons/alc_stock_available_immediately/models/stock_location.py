# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    exclude_from_immediately_usable_qty = fields.Boolean(
        "Exclude from immediately usable quantity", default=False, index=True
    )

    @api.model
    def get_excluded_from_immediately_usable_qty(self):
        """
        Returns the stock locations excluded from the immediately_usable qties
        """
        warehouses = self.env["stock.warehouse"].search([])
        stock_location_ids = warehouses.mapped("view_location_id").ids
        domain = [
            ("exclude_from_immediately_usable_qty", "=", True),
            ("id", "child_of", stock_location_ids),
        ]
        return self.search(domain)
