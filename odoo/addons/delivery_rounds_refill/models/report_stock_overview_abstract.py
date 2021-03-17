# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

import odoo.addons.decimal_precision as dp
from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class ReportStockOverview(models.AbstractModel):
    _name = "report.stock.overview.abstract"

    product_id = fields.Many2one("product.product", "Product")

    qty_in_bin = fields.Float("Quantity in bin")
    qty_in_bin_available = fields.Float("Quantity available in bin")
    qty_in_parking = fields.Float("Quantity in parking")
    qty_in_reserve = fields.Float("Quantity in reserve")

    confirmed_qty = fields.Integer(
        "Quantity to pick", help="Remaining quantity to pick"
    )
    confirmed_count = fields.Integer(
        "Customers to pick",
        help="Amount of customers having a remaining quantity to pick",
    )
    planned_qty = fields.Integer(
        "Planned quantity to pick",
        help="Remaining quantity to pick in a planned delivery round",
    )
    planned_count = fields.Integer(
        "Planned customers to pick",
        help="Amount of customers having a remaining quantity to pick"
        " in a planned delivery round",
    )
    immediate_qty = fields.Integer(
        "Immediate quantity to pick",
        help="Remaining quantity to pick in a stared delivery round",
    )
    immediate_count = fields.Integer(
        "Immediate customers to pick",
        help="Amount of customers having a remaining quantity to pick"
        " in a started delivery round",
    )
    refill_priority_arrange = fields.Integer("Arrangement Priority")
    refill_priority_reassort = fields.Integer("Reassortment Priority")
    safety_bin_min_qty = fields.Float(
        string="Min safety qty into bin",
        digits=dp.get_precision("Product Unit of Measure"),
        help="Minimal safety qty into a bin location",
    )
    abc_classification_level = fields.Selection(
        selection=ABC_SELECTION, required=True, read_only=True, index=True
    )
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", required=True)
