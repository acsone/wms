# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from extendable_pydantic import StrictExtendableBaseModel

from odoo.addons.sale.models import sale_order_line
from odoo.addons.shopinvader_schema_sale.schemas import sale_line


class SaleLineDiscount(StrictExtendableBaseModel):
    rate: float
    value: float

    @classmethod
    def from_sale_order_line(
        cls, odoo_rec: sale_order_line.SaleOrderLine
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable):
        return cls.model_construct(
            rate=odoo_rec.discount,
            value=odoo_rec.discount_total,
        )


class SaleLineUnitPrice(StrictExtendableBaseModel):
    untaxed: float
    untaxed_with_discount: float

    @classmethod
    def from_sale_order_line(
        cls, odoo_rec: sale_order_line.SaleOrderLine
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable):
        return cls.model_construct(
            untaxed=odoo_rec.price_unit,
            untaxed_with_discount=odoo_rec.price_unit
            - odoo_rec.price_unit * (odoo_rec.discount or 0) / 100,
        )


class SaleLine(sale_line.SaleLine, extends=True):
    discount: SaleLineDiscount | None = None
    unit_price: SaleLineUnitPrice | None = None

    @classmethod
    def from_sale_order_line(
        cls, odoo_rec: sale_order_line.SaleOrderLine
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order_line(odoo_rec)
        res.discount = SaleLineDiscount.from_sale_order_line(odoo_rec)
        res.unit_price = SaleLineUnitPrice.from_sale_order_line(odoo_rec)
        return res
