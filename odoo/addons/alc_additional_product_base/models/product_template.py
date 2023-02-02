# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields

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

    def _get_qty_additional_product(self, ordered_qty):
        self.ensure_one()

        if (
            not self.additional_product_id
            or not self.ratio_main_product
            or not self.ratio_additional_product
        ):
            return 0

        coefficient = int(ordered_qty / self.ratio_main_product)
        qty_additional_product = coefficient * self.ratio_additional_product

        return qty_additional_product
