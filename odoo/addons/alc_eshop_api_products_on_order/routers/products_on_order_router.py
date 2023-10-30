# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, HTTPException, Query

from odoo import _, api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..exceptions import NoBackOrderError
from ..models.alc_eshop_product_on_order import AlcEshopProductOnOrder
from ..schemas import (
    CancelProductOnOrderRequest,
    CancelProductOnOrderResponse,
    ProductFamily,
    ProductOnOrder,
    ProductOnOrderList,
    Restrict,
)

products_on_order_router = APIRouter(tags=["products_on_order"])


def _default_domain(
    partner: Annotated[Partner, Depends(authenticated_partner)]
) -> list:
    return [("partner_id", "=", partner.id)]


def _model(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)]
) -> AlcEshopProductOnOrder:
    return env["alc.eshop.product.on.order"]


# flake8: noqa: C901
@products_on_order_router.get("/products_on_order", status_code=200)
def get(
    domain: Annotated[list, Depends(_default_domain)],
    model: Annotated[AlcEshopProductOnOrder, Depends(_model)],
    customer_ref: str | None = None,
    order_date_max: datetime | None = None,
    order_date_min: datetime | None = None,
    order_ref: str | None = None,
    product_families: Annotated[list[ProductFamily] | None, Query()] = None,
    restricts: Annotated[list[Restrict] | None, Query()] = None,
    page: int | None = 1,
    per_page: int | None = 10,
) -> ProductOnOrderList:
    """Get products on order."""
    if customer_ref:
        domain.append(("customer_ref", "ilike", customer_ref))

    if order_date_max:
        domain.append(
            ("order_date", "<=", order_date_max.astimezone(pytz.timezone("UTC")))
        )
    if order_date_min:
        domain.append(
            ("order_date", ">=", order_date_min.astimezone(pytz.timezone("UTC")))
        )
    if order_ref:
        domain.append(("order_ref", "ilike", order_ref))
    if product_families:
        family_domain = []
        for product_family in product_families:
            if product_family == ProductFamily.meds:
                family_domain.append(("is_meds", "=", True))
            if product_family == ProductFamily.food:
                family_domain.append(("is_food", "=", True))
            if product_family == ProductFamily.equipment:
                family_domain.append(("is_equipment", "=", True))
            for _i in family_domain[:-1]:
                domain.append("|")
        domain.extend(family_domain)
    if restricts:
        restrict_domain = []
        for value in restricts:
            if value == Restrict.is_mto:
                restrict_domain.append(("is_mto", "=", True))
            if value == Restrict.has_backorder:
                restrict_domain.append(("has_backorder", "=", True))
        for _i in restrict_domain[:-1]:
            domain.append("|")
        domain.extend(restrict_domain)

    count = model.sudo().search_count(domain)
    offset = per_page * (page - 1)
    records = model.sudo().search(domain, limit=per_page, offset=offset)
    return {
        "size": count,
        "data": [
            ProductOnOrder.from_alc_eshop_product_on_order(record) for record in records
        ],
    }


@products_on_order_router.get("/products_on_order/{order_line_id}", status_code=200)
def get_for_order_line_id(
    domain: Annotated[list, Depends(_default_domain)],
    model: Annotated[AlcEshopProductOnOrder, Depends(_model)],
    order_line_id: int,
) -> ProductOnOrder:
    """Get products on order for specified order line."""
    domain.append(("order_line_id", "=", order_line_id))
    record = model.sudo().search(domain, limit=1)
    if not record:
        raise HTTPException(
            status_code=404, detail=f"Order line {order_line_id} not found"
        )
    return ProductOnOrder.from_alc_eshop_product_on_order(record)


@products_on_order_router.post(
    "/products_on_order/cancel/{order_line_id}", status_code=205
)
def cancel_order_line_id(
    domain: Annotated[list, Depends(_default_domain)],
    model: Annotated[AlcEshopProductOnOrder, Depends(_model)],
    order_line_id: int,
    rqst: CancelProductOnOrderRequest,
) -> CancelProductOnOrderResponse:
    """
    Request cancellation of specified order line.

        The cancellation is only possible for purchased products in back
        order
    """
    domain.append(("order_line_id", "=", order_line_id))
    record = model.sudo().search(domain, limit=1)
    if not record:
        return {
            "status": False,
            "error_msg": _("Requested order line no more exists"),
        }
    try:
        record.request_backorder_cancellation(quantity=rqst.quantity)
    except NoBackOrderError as error:
        return {"status": False, "error_msg": str(error)}
    return {"status": True}
