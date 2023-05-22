# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):

    _order = "sequence, name"

    sequence = fields.Integer(required=False)
