# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    sale_lines_count = fields.Integer(compute="_compute_sale_lines_count")

    @api.depends("product_variant_ids.sales_count")
    def _compute_sale_lines_count(self):
        for product in self:
            product.sale_lines_count = sum(
                p.sale_lines_count for p in product.product_variant_ids
            )
