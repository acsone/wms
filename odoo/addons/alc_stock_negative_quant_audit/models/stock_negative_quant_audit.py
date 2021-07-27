# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockNegativeQuantAudit(models.Model):

    _name = "stock.negative.quant.audit"
    _description = "Stock Negative Quant Audit"

    quant_id = fields.Many2one(
        comodel_name="stock.quant", required=True, ondelete="cascade"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="quant_id.product_id",
        store=True,
        ondelete="cascade",
    )
    stacktrace = fields.Text()
    user_id = fields.Many2one(comodel_name="res.users", required=True)
