# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    prepayment = fields.Boolean(
        "Prepayment",
        help="Check this if the invoice is received before reception of goods",
    )

    # pylint: disable=missing-return
    @api.depends(
        "state",
        "order_line.qty_invoiced",
        "order_line.qty_received",
        "order_line.product_qty",
        "prepayment",
    )
    def _get_invoiced(self):
        for order in self:
            if order.prepayment:
                order.invoice_status = "to invoice"
            else:
                super(PurchaseOrder, self)._get_invoiced()
