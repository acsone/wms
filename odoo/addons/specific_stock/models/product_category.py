# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    warning_info = fields.Char(
        string="Warning information",
        help="Additional information communicated to the customer",
        translate=True,
    )
