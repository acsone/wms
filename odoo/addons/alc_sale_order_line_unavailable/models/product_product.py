# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)

from .mixin_sales_lines_unavailable_action import MixinSaleLinesUnavailableAction


class ProductProduct(ProductProductBase, MixinSaleLinesUnavailableAction):
    _name = "product.product"

    def _get_view_sale_lines_unavailable_record_id_domain(self):
        self.ensure_one()
        return [("product_id", "=", self.id)]
