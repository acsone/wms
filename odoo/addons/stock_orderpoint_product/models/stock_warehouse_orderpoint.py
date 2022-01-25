# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockWarehouseOrderpoint(models.Model):

    _inherit = "stock.warehouse.orderpoint"

    _sql_constraints = [
        (
            "orderpoint_product_id_unique",
            "EXCLUDE (product_id WITH =) WHERE (active is true)",
            _("More than one active orderpoint for this product. Please archive one."),
        )
    ]
