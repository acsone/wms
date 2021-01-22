# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackOperationLotAdd(models.TransientModel):

    _inherit = "stock.pack.operation.lot.add"

    tracking = fields.Selection(related="product_id.tracking", readonly=True)
    lot_ids = fields.One2many(
        "stock.production.lot",
        string="Lots",
        related="product_id.lot_ids",
        readonly=True,
    )
    stock_bin_ids = fields.One2many(
        "product.stock.bin",
        string="Stock Bins",
        related="product_id.stock_bin_ids",
        readonly=True,
    )
