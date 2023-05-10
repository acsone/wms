# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .product_discount_special import ProductDiscountSpecial


class ProductTemplate(ProductTemplateBase):

    product_discount_special_ids = fields.One2many[ProductDiscountSpecial](
        inverse_name="product_template_id", copy=False, string="Discount Specials"
    )
