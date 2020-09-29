# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    product_qty_backorder = fields.Float(
        string="Qty into back order",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_product_qty_backorder",
        help="As long as no quantity has been delivered, the BO quantity is "
        "the quantity unavailable at the time of the order minus the canceled "
        "quantity. Otherwise it is the quantity remaining to be delivered.",
    )

    @api.multi
    @api.depends(
        "qty_delivered",
        "product_qty_canceled",
        "product_qty_unavailable",
        "product_qty_remains_to_deliver",
    )
    def _compute_product_qty_backorder(self):
        """
        As long as no quantity has been delivered, the BO quantity is the
        quantity unavailable at the time of the order minus the canceled
        quantity. Otherwise it is the quantity remaining to be delivered.
        """
        for record in self:
            if record.qty_delivered == 0 and record.product_qty_canceled == 0:
                record.product_qty_backorder = record.product_qty_unavailable
            else:
                record.product_qty_backorder = record.product_qty_remains_to_deliver
