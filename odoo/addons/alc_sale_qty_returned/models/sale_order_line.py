# Copyright 2018 Okia SPRL
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale_cancel_remaining.models.sale_order_line import (
    SaleOrderLine as SaleOrderLineBase,
)


class SaleOrderLine(SaleOrderLineBase):
    product_qty_returned = fields.Float(
        "Qty returned", readonly=True, copy=False, digits="Product Unit of Measure"
    )
