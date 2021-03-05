# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_qty_canceled = fields.Float(
        "Qty canceled",
        readonly=True,
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    product_qty_returned = fields.Float(
        "Qty returned",
        readonly=True,
        copy=False,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    product_qty_remains_to_deliver = fields.Float(
        string="Remains to deliver",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_product_qty_remains_to_deliver",
        store=True,
    )

    is_cancel_remaining_allowed = fields.Boolean(
        default=False, compute="_compute_is_cancel_remaining_allowed",
    )

    @api.multi
    @api.depends(
        "product_uom_qty",
        "qty_delivered",
        "product_qty_canceled",
        "product_qty_returned",
    )
    def _compute_product_qty_remains_to_deliver(self):
        for line in self:
            remaining_to_deliver = (
                line.product_uom_qty
                - line.qty_delivered
                - line.product_qty_canceled
                - line.product_qty_returned
            )
            line.product_qty_remains_to_deliver = remaining_to_deliver

    @api.multi
    @api.depends("product_id", "product_qty_remains_to_deliver", "qty_invoiced")
    def _compute_is_cancel_remaining_allowed(self):
        for line in self:
            if (
                line.product_id.product_tmpl_id.type in ["consu", "product"]
                and line.product_qty_remains_to_deliver != 0
                and line.qty_invoiced == 0
            ):
                line.is_cancel_remaining_allowed = True
            else:
                line.is_cancel_remaining_allowed = False
