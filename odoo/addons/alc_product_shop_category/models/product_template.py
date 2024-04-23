# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .product_category import ProductCategory


class ProductTemplate(ProductTemplateBase):

    categ_id = fields.Many2one[ProductCategory](domain=[("is_web", "=", False)])
    categ_ids = fields.Many2many[ProductCategory](domain=[("is_web", "=", True)])

    @api.constrains("categ_ids", "web_published")
    def _check_web_published_has_web_categories(self):
        for record in self:
            if not record.categ_ids and record.web_published:
                raise ValidationError(
                    _("A web category is required to publish a product on the website.")
                )
