# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields

from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    additional_product_id = fields.Many2one[ProductProduct](
        string="Additional Product", ondelete="restrict"
    )
    ratio_main_product = fields.Integer(string="Ratio Main Product")
    ratio_additional_product = fields.Integer(string="Ratio Additional Product")

    def get_qty_additional_product(self, ordered_qty):
        self.ensure_one()

        if (
            not self.additional_product_id
            or not self.ratio_main_product
            or not self.ratio_additional_product
        ):
            return 0

        coefficient = self.ratio_main_product / ordered_qty
        qty_additional_product = coefficient * self.ratio_additional_product

        return qty_additional_product

    @api.model
    def is_an_additional_product(self, product):
        # FIXME: is this used?
        return bool(self.search([("additional_product_id", "=", product.id)]))
