# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):
    def _prepare_promotional_line(self, qty):
        """Glue for promotional products and qty_unavailable.

        Recompute qty_unavailable for new promotional line.
        Promotional available quantity is computed after
        availability of main line.

        Thus there can be BO for promotional line even if
        there is no BO for ordered line.
        """
        res = super()._prepare_promotional_line(qty)
        qty_unavailable = self.get_product_qty_unavailable(
            self.product_id, self.product_uom_qty + qty, self.state == "sale", None
        )
        res["product_qty_unavailable"] = min(qty_unavailable, qty)
        return res
