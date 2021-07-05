# coding: utf-8
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    b2c_ref = fields.Char(related="gls_picking_id.sale_id.b2c_ref", readonly=True)
