# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    def write(self, vals):
        def _value(rec, field):
            return (
                rec[field].id
                if field in ["categ_id", "price_category_id"]
                else rec[field]
            )

        watched_fields = ["list_price", "categ_id", "price_category_id"]
        updated_fields = [f for f in watched_fields if f in vals]
        to_update = self.filtered(
            lambda product: any(
                _value(product, field) != vals[field] for field in updated_fields
            )
        )
        res = super().write(vals)
        if to_update:
            to_update.mapped("product_variant_ids")._delay_update_price_cache()
        return res
