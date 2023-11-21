# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from extendable_pydantic.models import StrictExtendableBaseModel

from odoo.addons.shopinvader_schema_sale.schemas import sale_line


class SaleLineProduct(StrictExtendableBaseModel):
    name: str
    sku: str | None


class SaleLine(sale_line.SaleLine, extends=True):
    product: SaleLineProduct | None = None

    @classmethod
    def from_sale_order_line(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order_line(odoo_rec)
        if odoo_rec.product_id:
            res.product = SaleLineProduct(
                name=odoo_rec.product_id.name,
                sku=odoo_rec.product_id.default_code or None,
            )
        return res
