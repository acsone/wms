# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.product.models.product_product import ProductProduct as Product


class ProductProduct(Product):
    """Will be overriden by corresponding alce module."""

    has_intrastat = fields.Boolean(string="Intrastat ok")
    intrastat_code_name = fields.Char(string="Intrastat Code")
