# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from odoo.addons.alc_eshop_schema_sale_product_unavailable import schemas


class SaleLine(schemas.SaleLine, extends=True):
    @classmethod
    def from_sale_order_line(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order_line(odoo_rec)
        if odoo_rec.product_id.is_human:
            res.qty_unavailable = 0.0
        return res
