# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .product_supplierinfo import ProductSupplierInfo


class ProductTemplate(ProductTemplateBase):

    supplier_promotion_ids = fields.One2many[ProductSupplierInfo](
        compute="_compute_seller_ids_subfields"
    )
    supplier_discount_ids = fields.One2many[ProductSupplierInfo](
        compute="_compute_seller_ids_subfields"
    )

    @api.depends("seller_ids")
    def _compute_seller_ids_subfields(self):
        for product in self:
            current_info = product.seller_ids.filtered(lambda si: not si.is_past)
            product.supplier_promotion_ids = current_info.filtered("is_promotion")
            product.supplier_discount_ids = current_info.filtered("is_sale_discount")
