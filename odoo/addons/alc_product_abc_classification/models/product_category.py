# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):

    _inherit = "product.category"

    abc_classification_profile_ids = fields.Many2many("abc.classification.profile")
    product_variant_ids = fields.One2many("product.product", inverse_name="categ_id")
