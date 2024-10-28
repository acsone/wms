# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tools import drop_index, index_exists

from odoo.addons.product.models import product_product


class ProductProduct(product_product.ProductProduct):

    default_code = fields.Char(index=False)

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "product_product_uniq_default_code",
        ):
            # covered by the previous index
            drop_index(
                self._cr, "product_product_default_code_index", "product_product"
            )
