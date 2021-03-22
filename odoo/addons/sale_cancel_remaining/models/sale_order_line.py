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
