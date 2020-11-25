# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductStockBin(models.Model):
    _name = "product.stock.bin"
    _order = "sequence"

    sequence = fields.Integer("Seq.")
    location_id = fields.Many2one(
        "stock.location", "Location", required=True, ondelete="restrict"
    )
    bin_location_id = fields.Many2one(
        "stock.location", "Bin", required=True, ondelete="restrict"
    )
    product_id = fields.Many2one(
        "product.template", "Product", required=True, ondelete="cascade"
    )
