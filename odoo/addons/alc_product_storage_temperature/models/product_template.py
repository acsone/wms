# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .product_storage_temperature import ProductStorageTemperature


class ProductTemplate(ProductTemplateBase):

    storage_temperature_id = fields.Many2one[ProductStorageTemperature](
        string="Storage temperature"
    )
