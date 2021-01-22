# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"
    lot_ids = fields.One2many(
        "stock.production.lot", string="Lots", inverse_name="product_id", readonly=True,
    )
