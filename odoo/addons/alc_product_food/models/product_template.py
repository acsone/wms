# Copyright 2023 ACSONE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_product_category_property.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    is_food = fields.Boolean(
        string="Food",
        compute="_compute_is_food",
        store=True,
    )

    @api.depends("categ_id")
    def _compute_is_food(self):
        self._compute_business_unit_property(
            "is_food", "alc_product_category_data.product_categ_ali"
        )
