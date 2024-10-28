# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tools import drop_index, index_exists

from odoo.addons.product.models import product_attribute


class ProductTemplateAttributeValue(product_attribute.ProductTemplateAttributeValue):

    attribute_line_id = fields.Many2one[product_attribute.ProductTemplateAttributeLine](
        index=False
    )

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "product_template_attribute_value_attribute_value_unique",
        ):
            # covered by the previous index
            drop_index(
                self._cr,
                "product_template_attribute_value_attribute_line_id_index",
                "product_template_attribute_value",
            )
