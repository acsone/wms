# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_business_unit = fields.Boolean('Business Unit')
    turnover = fields.Float('Turnover')
