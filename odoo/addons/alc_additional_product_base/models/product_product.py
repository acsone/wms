# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):
    def _get_qty_additional_product(self, ordered_qty):
        self.ensure_one()
        return self.product_tmpl_id._get_qty_additional_product(ordered_qty)
