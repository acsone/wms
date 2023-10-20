# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_quant import StockQuant as StockQuantBase


class StockQuant(StockQuantBase):
    product_last_in_date = fields.Datetime(
        "Last Purchasing Date", related="product_id.product_last_in_date", readonly=True
    )
    product_last_out_date = fields.Datetime(
        "Last Selling Date", related="product_id.product_last_out_date", readonly=True
    )
