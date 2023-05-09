# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):

    is_web = fields.Boolean(compute="_compute_is_web", store=True)

    @api.depends("parent_id")  # insufficient depends, recursive property; see write
    def _compute_is_web(self):
        xml_id = "alc_product_shop_category.master"
        web_root_id = self.env["ir.model.data"]._xmlid_to_res_id(xml_id)  # init
        web_categories = []
        if web_root_id:
            web_categories = self.search([("parent_id", "child_of", web_root_id)])
        for category in self:
            category.is_web = category in web_categories

    def write(self, vals):
        is_webs = self.mapped("is_web")
        res = super().write(vals)
        if self.mapped("is_web") != is_webs:
            children = self.search([("parent_id", "child_of", self.ids)])
            children._compute_is_web()
        return res
