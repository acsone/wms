# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from pydantic import BaseModel

from odoo.tools.float_utils import float_round

from odoo.addons.delivery.models import delivery_carrier, sale_order
from odoo.addons.shopinvader_schema_sale import schemas


class DeliveryMethod(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    id: int
    name: str

    @classmethod
    def from_delivery_carrier(
        cls, record: delivery_carrier.DeliveryCarrier
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            id=record.id,
            name=record.name,
        )


class DeliveryAmount(schemas.SaleAmount):
    @classmethod
    def from_sale_order(cls, odoo_rec: sale_order.SaleOrder):
        precision = odoo_rec.currency_id.decimal_places
        total = float_round(odoo_rec.shipping_amount_total, precision)
        return cls.model_construct(
            tax=float_round(odoo_rec.shipping_amount_tax, precision),
            untaxed=float_round(odoo_rec.shipping_amount_untaxed, precision),
            total=total,
            total_without_discount=total,
            discount_total=0.0,
        )


class DeliveryInfo(schemas.DeliveryInfo, extends=True):
    method: DeliveryMethod | None = None
    fees: DeliveryAmount | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        if odoo_rec.carrier_id:
            res.method = DeliveryMethod.from_delivery_carrier(odoo_rec.carrier_id)
            res.fees = DeliveryAmount.from_sale_order(odoo_rec)
        return res


class Sale(schemas.Sale, extends=True):
    amount_without_delivery: schemas.SaleAmount | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        res = super().from_sale_order(odoo_rec)
        res.amount_without_delivery = cls._get_amount_without_delivery(odoo_rec)
        return res

    @classmethod
    def _get_amount_without_delivery(cls, sale) -> schemas.SaleAmount:
        precision = sale.currency_id.decimal_places
        tax = sale.amount_tax - sale.shipping_amount_tax
        untaxed = sale.amount_untaxed - sale.shipping_amount_untaxed
        total = sale.discount_total - sale.shipping_amount_total
        total_without_discount = total - sale.discount_total
        return schemas.SaleAmount.model_construct(
            tax=float_round(tax, precision),
            untaxed=float_round(untaxed, precision),
            total=float_round(total, precision),
            total_without_discount=float_round(total_without_discount, precision),
            discount_total=0.0,
        )
