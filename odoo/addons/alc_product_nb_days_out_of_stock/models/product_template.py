# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.sale.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    nb_days_out_of_stock = fields.Integer(
        help="Number of days before running out of stock",
        compute="_compute_date_out_of_stock",
    )

    @api.depends("route_ids", "product_variant_ids")
    def _compute_date_out_of_stock(self):
        for product in self:
            if product.product_variant_count > 1:
                product.nb_days_out_of_stock = 0
            else:
                product.nb_days_out_of_stock = (
                    product.product_variant_id.nb_days_out_of_stock
                )
