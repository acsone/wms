# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from slugify import slugify

from odoo import fields, models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    role_name = fields.Char(compute="_compute_role_name", store=False)
    discount_role_name = fields.Char(compute="_compute_role_name", store=False)

    def _compute_role_name(self):
        for pl in self:
            role_name = slugify("price_" + pl.name)
            pl.role_name = role_name
            pl.discount_role_name = "discount_%s" % role_name
