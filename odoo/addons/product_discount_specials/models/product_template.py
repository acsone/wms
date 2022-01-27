# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    product_discount_special_ids = fields.One2many(
        "product.discount.special", "product_template_id", copy=False
    )
