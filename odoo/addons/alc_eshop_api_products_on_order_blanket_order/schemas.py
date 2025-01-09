# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from odoo.addons.alc_eshop_api_products_on_order import schemas

from .models.alc_eshop_product_on_order import AlcEshopProductOnOrder


class ProductOnOrder(schemas.ProductOnOrder):

    @classmethod
    def from_alc_eshop_product_on_order(
        cls, row: AlcEshopProductOnOrder
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        inst = super().from_alc_eshop_product_on_order(row)
        # A hack to display the remaining qty to deliver as
        # ordered qty for blanket orders and the remaining qty
        # available for call-off as backorder qty.
        if row.order_id.order_type == "blanket":
            line = row.order_line_id
            inst.qty_in_backorder = line.call_off_remaining_qty
            inst.qty_ordered = inst.qty_to_deliver
        return inst
