# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    supplier_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        readonly=True,
        related="product_tmpl_id.supplier_id",
    )
