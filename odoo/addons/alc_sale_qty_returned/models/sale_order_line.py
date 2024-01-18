# Copyright 2018 Okia SPRL
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.sale_order_line_cancel.models.sale_order_line import (
    SaleOrderLine as SaleOrderLineBase,
)


class SaleOrderLine(SaleOrderLineBase):
    product_qty_returned = fields.Float(
        "Qty returned", readonly=True, copy=False, digits="Product Unit of Measure"
    )

    @api.depends("product_qty_returned")
    def _compute_product_qty_remains_to_deliver(self):
        res = super()._compute_product_qty_remains_to_deliver()
        for rec in self:
            rec.product_qty_remains_to_deliver -= rec.product_qty_returned
        return res
