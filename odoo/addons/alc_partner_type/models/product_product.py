# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)

from .product_partner_type import ProductPartnerType


class ProductProduct(ProductProductBase, ProductPartnerType):

    _name = "product.product"
