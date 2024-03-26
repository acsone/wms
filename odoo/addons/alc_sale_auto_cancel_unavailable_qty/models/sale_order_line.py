# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):
    def _get_qty_procurement(self, previous_product_uom_qty=False):
        self.ensure_one()
        qty = super()._get_qty_procurement(
            previous_product_uom_qty=previous_product_uom_qty
        )
        if (
            self.order_partner_id.auto_cancel_unavailable_qty_sold
            and self.product_id.type != "service"
            and self.product_qty_unavailable
        ):
            # To avoid further new moves if original quantity was already cancelled
            # we don't take into account that cancelled one.
            qty += self.product_qty_unavailable - self.product_qty_canceled
            self.product_qty_canceled = self.product_qty_unavailable
        return qty
