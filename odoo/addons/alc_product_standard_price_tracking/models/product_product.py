# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):

    standard_price = fields.Float(tracking=True)
