# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackOperationLotAdd(models.TransientModel):

    _inherit = "stock.pack.operation.lot.add"

    product_stock_storage_type_id = fields.Many2one(
        related="product_id.product_tmpl_id.product_package_storage_type_id",
        readonly=True,
    )
