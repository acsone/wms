# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):

    _inherit = "product.category"

    is_web = fields.Boolean(compute="_compute_is_web", store=True)

    @api.depends("parent_id")  # insufficient depends, recursive property; see write
    def _compute_is_web(self):
        xml_id = "alc_product_shop_category.master"
        web_root = self.env.ref(xml_id, raise_if_not_found=False)  # init
        web_categories = []
        if web_root:
            web_categories = self.search([("parent_id", "child_of", web_root.id)])
        for category in self:
            category.is_web = category in web_categories

    def write(self, vals):
        is_webs = self.mapped("is_web")
        res = super(ProductCategory, self).write(vals)
        if self.mapped("is_web") != is_webs:
            children = self.search([("parent_id", "child_of", self.ids)])
            children._compute_is_web()
        return res
