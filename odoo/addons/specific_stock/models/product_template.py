# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    life_time = fields.Integer(related="categ_id.life_time")

    use_time = fields.Integer(related="categ_id.use_time")

    removal_time = fields.Integer(related="categ_id.removal_time")

    alert_time = fields.Integer(related="categ_id.alert_time")

    picking_zone_id = fields.Many2one(
        "picking.zone",
        string="Picking zone",
        compute="_compute_picking_zone_id",
        readonly=True,
        store=True,
    )
    is_mto_product = fields.Boolean(
        "On Order", readonly=True, compute="_compute_picking_zone_id", store=True
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
            product_routes = product.route_ids | product.categ_id.total_route_ids

            product.is_mto_product = route_mto in product_routes
            # We need to remove the MTO route because this route has a higher
            # priority but we want to compute the picking zone only on
            # "standard" route
            product_routes -= route_mto

            res = Rule.search(
                [
                    ("route_id", "in", product_routes.ids),
                    ("picking_type_id", "in", picking_types.ids),
                ],
                order="route_sequence, sequence",
                limit=1,
            )
            if res:
                product.picking_zone_id = res.picking_type_id.picking_zone_id.id
