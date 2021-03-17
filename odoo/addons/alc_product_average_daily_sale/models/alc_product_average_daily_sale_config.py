# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class AlcProductAverageDailySaleConfig(models.Model):

    _name = "alc.product.average.daily.sale.config"
    _description = "Average daily sales computation parameters"

    abc_classification_level = fields.Selection(
        selection=ABC_SELECTION, required=True, read_only=True
    )
    stddev_exclude_factor = fields.Float(
        string="Standard deviation exclude factor", required=True, digits=(2, 2)
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.user.company_id.id)], limit=1
        ),
        readonly=True,
    )
    period_name = fields.Selection(
        string="Period analyzed unit",
        selection=[
            ("year", "Years"),
            ("month", "Months"),
            ("week", "Weeks"),
            ("day", "Days"),
        ],
        required=True,
    )
    period_value = fields.Integer("Period analyzed value", required=True)
    number_days_qty_in_stock = fields.Integer(
        string="Number of days of quantities in stock", required=True, default=2
    )
    safety_factor = fields.Float(
        digits=(2, 2), required=True, oldname="stddev_include_factor"
    )
