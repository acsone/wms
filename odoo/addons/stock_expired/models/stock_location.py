# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    ignore_quants_expiration = fields.Boolean(
        string='Ignore quants expiration'
    )
