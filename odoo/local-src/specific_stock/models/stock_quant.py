# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    supplier_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        readonly=True,
        related='product_id.supplier_id')
