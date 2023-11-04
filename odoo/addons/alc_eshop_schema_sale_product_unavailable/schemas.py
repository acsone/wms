# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from odoo.addons.shopinvader_schema_sale.schemas import sale_order


class SaleOrderLine(sale_order.SaleOrderLine, extends=True):
    qty_unavailable: float = 0.0

    @classmethod
    def from_sale_order_line(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order_line(odoo_rec)
        res.qty_unavailable = odoo_rec.product_qty_unavailable or 0.0
        return res
