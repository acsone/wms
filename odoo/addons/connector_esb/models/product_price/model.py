# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Store the calculated field sale_price_2 from product_template before
    # the esb export, so the write_date is changed and the product exported
    sale_price_2_export = fields.Float(string="Sale Price 2 exported")
