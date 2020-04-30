# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'
    _description = 'Tax'
    _order = 'sequence,id'

    # Rise decimal precision from (16, 4) to (16, 5)
    # the APB taxe needs a precision of 5 decimals
    amount = fields.Float(required=True, digits=(16, 5))
