# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    picking_zone_id = fields.Many2one(
        "picking.zone",
        string="Picking zone",
        compute="_compute_picking_zone_id",
        readonly=True,
        store=True,
    )

    @api.depends("route_ids", "route_from_categ_ids")
    def _compute_picking_zone_id(self):
        Rule = self.env["procurement.rule"]
        stock_location = self.env.ref("stock.stock_location_stock")
        picking_types = self.env["stock.picking.type"].search(
            [("default_location_src_id", "child_of", stock_location.id)]
        )
        route_mto = self.env.ref("stock.route_warehouse0_mto")

        for product in self:
            product.picking_zone_id = False
            product_routes = product.route_ids | product.categ_id.total_route_ids

            # We need to remove the MTO route because this route has a higher
            # priority but we want to compute the picking zone only on
            # "standard" route
            product_routes -= route_mto

            res = Rule
            if product_routes and picking_types:
                res = Rule.search(
                    [
                        ("route_id", "in", product_routes.ids),
                        ("picking_type_id", "in", picking_types.ids),
                    ],
                    order="route_sequence, sequence",
                    limit=1,
                )
            product.picking_zone_id = res.picking_type_id.picking_zone_id.id
