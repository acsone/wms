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
        food_category = self.env.ref(
            "alc_product_food.product_categ_ali", raise_if_not_found=False
        )
        for product in self:
            category = product.categ_id
            is_food = False
            if category and food_category:
                cat_parent_ids = [
                    int(cat_id) for cat_id in category.parent_path.split("/") if cat_id
                ]
                is_food = (
                    category == food_category or food_category.id in cat_parent_ids
                )
            product.is_food = is_food
