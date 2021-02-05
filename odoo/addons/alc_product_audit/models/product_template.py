# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    no_min_max_no_on_command_reappro = fields.Boolean(
        default=False,
        compute="_compute_min_max_and_on_command_reappro",
        store=True,
        index=True,
    )
    min_max_on_command_reappro = fields.Boolean(
        default=False,
        compute="_compute_min_max_and_on_command_reappro",
        store=True,
        index=True,
    )
    sale_not_ok_not_archived = fields.Boolean(
        default=False,
        compute="_compute_sale_not_ok_not_archived",
        store=True,
        index=True,
    )
    sale_not_ok_archived_bin_available = fields.Boolean(
        default=False,
        compute="_compute_sale_not_ok_archived_bin_available",
        store=True,
        index=True,
    )

    mismatch_route_picking = fields.Boolean(
        default=False, compute="_compute_mismatch_route_picking", store=True, index=True
    )

    mismatch_picking_bin = fields.Boolean(
        default=False, compute="_compute_mismatch_picking_bin", store=True, index=True
    )

    mto_with_abnormal_route = fields.Boolean(
        default=False,
        compute="_compute_mto_with_abnormal_route",
        store=True,
        index=True,
    )

    can_be_bought_without_buy_route = fields.Boolean(
        default=False,
        compute="_compute_can_be_bought_without_buy_route",
        store=True,
        index=True,
    )

    has_no_dimensions = fields.Boolean(
        default=False, compute="_compute_has_no_dimensions", store=True, index=True,
    )

    packaging_has_no_dimensions = fields.Boolean(
        default=False,
        compute="_compute_packaging_has_no_dimensions",
        store=True,
        index=True,
    )

    has_anomaly = fields.Boolean(
        default=False, compute="_compute_has_anomaly", store=True, index=True
    )

    @api.depends("route_ids", "orderpoint_min", "orderpoint_max")
    def _compute_min_max_and_on_command_reappro(self):
        on_command_reappro_route = self.env.ref("stock.route_warehouse0_mto")
        for product in self:
            if product.type == "service":
                # No min/max or reappro rule on services
                continue

            if (
                not product.orderpoint_min
                and not product.orderpoint_max
                and not (on_command_reappro_route in product.route_ids)
            ):
                product.no_min_max_no_on_command_reappro = True
            else:
                product.no_min_max_no_on_command_reappro = False

            if (
                product.orderpoint_min
                and product.orderpoint_max
                and on_command_reappro_route in product.route_ids
            ):
                product.min_max_on_command_reappro = True
            else:
                product.min_max_on_command_reappro = False

    @api.depends("sale_ok", "active")
    def _compute_sale_not_ok_not_archived(self):
        for product in self:
            if not product.sale_ok and product.active:
                product.sale_not_ok_not_archived = True
            else:
                product.sale_not_ok_not_archived = False

    @api.depends("sale_ok", "active", "stock_bin_ids")
    def _compute_sale_not_ok_archived_bin_available(self):
        for product in self:
            if product.stock_bin_ids and not (product.sale_ok and product.active):
                product.sale_not_ok_archived_bin_available = True
            else:
                product.sale_not_ok_archived_bin_available = False

    @api.depends("purchase_ok", "route_ids")
    def _compute_can_be_bought_without_buy_route(self):
        purchase_route = self.env.ref("purchase.route_warehouse0_buy")
        for product in self:
            product_routes = product.route_ids
            if product.purchase_ok and purchase_route not in product_routes:
                product.can_be_bought_without_buy_route = True
            else:
                product.can_be_bought_without_buy_route = False

    @api.depends("route_ids")
    def _compute_mismatch_route_picking(self):
        Rule = self.env["procurement.rule"]
        stock_location = self.env.ref("stock.stock_location_stock")
        picking_types = self.env["stock.picking.type"].search(
            [("default_location_src_id", "child_of", stock_location.id)]
        )
        for product in self:
            product_routes = product.route_ids

            res = Rule.search(
                [
                    ("route_id", "in", product_routes.ids),
                    ("picking_type_id", "in", picking_types.ids),
                ],
                order="route_sequence, sequence",
            )
            if len(res) > 1:
                product.mismatch_route_picking = True
            else:
                product.mismatch_route_picking = False

    @api.depends("picking_zone_id", "stock_bin_ids")
    def _compute_mismatch_picking_bin(self):
        for product in self:
            if product.stock_bin_ids:
                for stock_bin in product.stock_bin_ids:
                    if (
                        stock_bin.bin_location_id.picking_zone_id
                        != product.picking_zone_id
                    ):
                        product.mismatch_picking_bin = True
                    else:
                        product.mismatch_picking_bin = False

    @api.depends("route_ids")
    def _compute_mto_with_abnormal_route(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto")
        new_route = self.env.ref(
            "__setup__.stock_location_route_new", raise_if_not_found=False
        )
        for product in self:
            product_routes = product.route_ids
            if (
                mto_route in product_routes
                and new_route
                and new_route in product_routes
            ):
                product.mto_with_abnormal_route = True
            else:
                product.mto_with_abnormal_route = False

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.height",
        "product_variant_ids.length",
        "product_variant_ids.width",
    )
    def _compute_has_no_dimensions(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for product in unique_variants:
            if product.type == "service":
                # No dimensions on services
                continue

            if not product.length or not product.width or not product.height:
                product.has_no_dimensions = True
            else:
                product.has_no_dimensions = False
        for product in self - unique_variants:
            product.has_no_dimensions = False

    @api.depends(
        "packaging_ids",
        "packaging_ids.height",
        "packaging_ids.lngth",
        "packaging_ids.width",
    )
    def _compute_packaging_has_no_dimensions(self):
        missing_dimensions = []
        for product in self:
            if product.type == "service":
                # No dimensions on services
                continue

            packagings = product.mapped("packaging_ids")
            if packagings:
                for pack in packagings:
                    if not pack.lngth or not pack.width or not pack.height:
                        missing_dimensions.append(True)
                    else:
                        missing_dimensions.append(False)
                if any(missing_dimensions):
                    product.packaging_has_no_dimensions = True
                else:
                    product.packaging_has_no_dimensions = False
            else:
                product.packaging_has_no_dimensions = False

    @api.depends(
        "min_max_on_command_reappro",
        "no_min_max_no_on_command_reappro",
        "sale_not_ok_not_archived",
        "sale_not_ok_archived_bin_available",
        "mismatch_route_picking",
        "mismatch_picking_bin",
        "mto_with_abnormal_route",
        "can_be_bought_without_buy_route",
        "has_no_dimensions",
        "packaging_has_no_dimensions",
    )
    def _compute_has_anomaly(self):
        for product in self:
            if (
                product.mismatch_route_picking
                or product.mismatch_picking_bin
                or product.sale_not_ok_archived_bin_available
                or product.sale_not_ok_not_archived
                or product.min_max_on_command_reappro
                or product.no_min_max_no_on_command_reappro
                or product.mto_with_abnormal_route
                or product.can_be_bought_without_buy_route
                or product.has_no_dimensions
                or product.packaging_has_no_dimensions
            ):
                product.has_anomaly = True
            else:
                product.has_anomaly = False
