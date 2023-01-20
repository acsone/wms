# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):

    is_business_unit = fields.Boolean("Business Unit")
