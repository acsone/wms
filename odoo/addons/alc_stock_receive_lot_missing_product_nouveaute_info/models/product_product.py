# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"
    no_barcode_authorized = fields.Boolean(
        default=False,
        string="Without barcode",
        help="Product allowed to be without barcode",
    )
