# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    is_additional_line = fields.Boolean('Is Additional Line')
