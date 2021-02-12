# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_mto_product = fields.Boolean(
        "On Order", readonly=True, compute="_compute_is_mto_product", store=True,
    )

    @api.depends("route_ids", "route_from_categ_ids")
    def _compute_is_mto_product(self):
        route_mto = self.env.ref("stock.route_warehouse0_mto")
        for product in self:
            product_routes = product.route_ids | product.categ_id.total_route_ids
            product.is_mto_product = route_mto in product_routes
