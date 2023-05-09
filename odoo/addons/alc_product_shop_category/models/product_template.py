# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .product_category import ProductCategory


class ProductTemplate(ProductTemplateBase):

    categ_id = fields.Many2one[ProductCategory](domain=[("is_web", "=", False)])
    categ_ids = fields.Many2many[ProductCategory](domain=[("is_web", "=", True)])
