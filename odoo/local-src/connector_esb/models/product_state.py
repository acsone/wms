# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductState(models.Model):
    _inherit = 'product.state'

    esb_ref = fields.Char(string='Reference for ESB', copy=False)
