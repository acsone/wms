# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):

    is_business_unit = fields.Boolean("Business Unit")

    def write(self, vals):
        res = super().write(vals)
        if "parent_id" in vals or "is_business_unit" in vals:
            self.flush_recordset()
            # the compute of business_unit_id in product.product uses sql query
            self.env["product.product"].invalidate_model(["business_unit_id"])
            self.env["product.template"].invalidate_model(["business_unit_id"])
        return res
