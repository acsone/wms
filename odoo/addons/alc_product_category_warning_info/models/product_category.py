# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):

    warning_info = fields.Char(
        string="Warning information",
        help="Additional information communicated to the customer",
        translate=True,
    )
