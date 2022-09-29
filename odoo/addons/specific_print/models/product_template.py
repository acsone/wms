# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    number_labels_to_print = fields.Integer(
        default=1, string="Number of Labels to Print."
    )
