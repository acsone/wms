# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import (
    Subscription,
    SubscriptionList,
    SubscriptionRequest,
    SubscriptionStatus,
)

promo_subscriptions_router = APIRouter(tags=["promo_subscriptions"])


@promo_subscriptions_router.post("/promo_subscriptions", status_code=205)
def subscribe(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    rqst: SubscriptionRequest,
) -> SubscriptionStatus:
    """Subscribe the customer to the promotions for the given product id."""
    product = env["product.product"].sudo().browse(rqst.product_id)
    env["alc.product.promotion.subscription"].sudo().subscribe(
        partner=partner, product=product
    )
    return {"status": True}


@promo_subscriptions_router.get("/promo_subscriptions")
def get_all_subscriptions(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    product_id: int | None = None,
    page: int | None = 1,
    per_page: int | None = 10,
) -> SubscriptionList:
    """Get all the products the customer has subscribed to."""
    domain = [("partner_id", "=", partner.id)]
    if product_id:
        domain.append(("product_id", "=", product_id))
    count = env["alc.product.promotion.subscription"].sudo().search_count(domain)
    offset = (page - 1) * per_page
    subscriptions = (
        env["alc.product.promotion.subscription"]
        .sudo()
        .search(domain, limit=per_page, offset=offset)
    )
    return SubscriptionList(
        size=count,
        data=[
            Subscription(
                product_id=subscription.product_id.id,
            )
            for subscription in subscriptions
        ],
    )


@promo_subscriptions_router.get("/promo_subscriptions/{product_id}")
def get_status(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    product_id: int,
) -> SubscriptionStatus:
    """Check if a subscription exists for the given product_id."""
    record = (
        env["alc.product.promotion.subscription"]
        .sudo()
        .search([("partner_id", "=", partner.id), ("product_id", "=", product_id)])
    )
    status = bool(record)
    return {"status": status}


@promo_subscriptions_router.delete("/promo_subscriptions/{product_id}", status_code=204)
def unsubscribe(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    product_id: int,
) -> None:
    """
    Unsubscribe the customer to the promotions of the given product.

        id.
    """
    product = env["product.product"].sudo().browse(product_id)
    env["alc.product.promotion.subscription"].sudo().unsubscribe(
        partner=partner, product=product
    )
