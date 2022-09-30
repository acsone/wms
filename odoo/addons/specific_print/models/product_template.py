# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    number_labels_to_print = fields.Integer(
        default=1,
        string="Number of Labels to Print.",
        help="This field determines how many Product/Customer labels to print, "
        "and only these labels. Set to 0 to skip printing any.",
    )
