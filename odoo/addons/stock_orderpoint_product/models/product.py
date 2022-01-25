# -*- coding: utf-8 -*-
# © 2016 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    orderpoint_qty_multiple = fields.Float(
        "Qty Multiple",
        compute="_compute_orderpoint",
        inverse="_inverse_orderpoint",
        store=True,
    )

    orderpoint_min = fields.Float(
        "Minimum Quantity",
        compute="_compute_orderpoint",
        inverse="_inverse_orderpoint",
        store=True,
    )
    orderpoint_max = fields.Float(
        "Maximum Quantity",
        compute="_compute_orderpoint",
        inverse="_inverse_orderpoint",
        store=True,
    )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.orderpoint_qty_multiple",
        "product_variant_ids.orderpoint_min",
        "product_variant_ids.orderpoint_max",
    )
    def _compute_orderpoint(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            product = template.product_variant_ids
            template.orderpoint_min = product.orderpoint_min
            template.orderpoint_max = product.orderpoint_max
            template.orderpoint_qty_multiple = product.orderpoint_qty_multiple

        for template in self - unique_variants:
            template.orderpoint_min = 0
            template.orderpoint_max = 0
            template.orderpoint_qty_multiple = 0

    def _inverse_orderpoint(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_id.write(
                {
                    "orderpoint_min": self.orderpoint_min,
                    "orderpoint_max": self.orderpoint_max,
                    "orderpoint_qty_multiple": self.orderpoint_qty_multiple,
                }
            )


class ProductProduct(models.Model):
    _inherit = "product.product"

    orderpoint_qty_multiple = fields.Float(
        "Qty Multiple",
        compute="_compute_orderpoint",
        inverse="_inverse_orderpoint",
        store=True,
    )
    orderpoint_min = fields.Float(
        "Minimum Quantity",
        compute="_compute_orderpoint",
        inverse="_inverse_orderpoint",
        store=True,
    )
    orderpoint_max = fields.Float(
        "Maximum Quantity",
        compute="_compute_orderpoint",
        inverse="_inverse_orderpoint",
        store=True,
    )

    def _create_orderpoint(self, product):
        return self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": product.id,
                "product_uom": product.uom_id,
                "product_min_qty": product.orderpoint_min,
                "product_max_qty": product.orderpoint_max,
                "qty_multiple": product.orderpoint_qty_multiple,
                "active": product.active,
                "location_id": self.env.ref(
                    "stock.stock_location_stock"
                ).location_id.id,
            }
        )

    @api.depends(
        "orderpoint_ids",
        "orderpoint_ids.qty_multiple",
        "orderpoint_ids.product_min_qty",
        "orderpoint_ids.active",
        "orderpoint_ids.product_max_qty",
    )
    def _compute_orderpoint(self):
        for product in self:
            orderpoints = product.orderpoint_ids.filtered(lambda o: o.active)
            if orderpoints:
                orderpoint = orderpoints[0]
                product.orderpoint_min = orderpoint.product_min_qty
                product.orderpoint_max = orderpoint.product_max_qty
                product.orderpoint_qty_multiple = orderpoint.qty_multiple
            else:
                product.orderpoint_min = 0.0
                product.orderpoint_max = 0.0
                product.orderpoint_qty_multiple = 0.0

    def _inverse_orderpoint(self):
        for product in self:
            orderpoints = product.orderpoint_ids.filtered(lambda o: o.active)
            if orderpoints:
                orderpoint = orderpoints[0]
                orderpoint.write(
                    {
                        "product_min_qty": product.orderpoint_min,
                        "product_max_qty": product.orderpoint_max,
                        "qty_multiple": product.orderpoint_qty_multiple,
                    }
                )
            else:
                self._create_orderpoint(product)
