# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from odoo import api
from odoo.osv.expression import AND

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import PagedCollection, Paging

from ..schemas import LoyaltyCard, LoyaltyCardHistory

loyalty_card_router = APIRouter(tags=["loyalty_card"])


@loyalty_card_router.get("/loyalty/card/rfa/current")
def get_current_loyalty_card_rfa(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> LoyaltyCard:
    """Get current RFA info."""

    domain = partner.sudo()._get_loyalty_card_domain()
    cards = (
        env["loyalty.card"]
        .sudo()
        .search(
            AND(
                [
                    domain,
                    [
                        ("program_type", "=", "year_end_rebate"),
                    ],
                ]
            )
        )
    )
    if cards:
        now = date.today()
        cards = cards.filtered(
            lambda card, n=now: card.program_id.date_from
            <= n
            <= card.program_id.date_to
        )
    if not cards:
        return Response(status_code=204)
    card = cards[0]
    return LoyaltyCard.from_loyalty_card(card)


@loyalty_card_router.get("/loyalty/card/{card_id}/history")
def get_loyalty_card_history(
    paging_: Annotated[Paging, Depends(paging)],
    card_id: int,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> PagedCollection[LoyaltyCardHistory]:
    """Get loyalty card points assignation history."""
    domain = partner.sudo()._get_loyalty_card_domain()
    domain = AND(
        [
            domain,
            [
                ("id", "=", card_id),
            ],
        ]
    )
    card = env["loyalty.card"].sudo().search(domain=domain, limit=1)
    if not card:
        return Response(status_code=404)
    domain = [("coupon_id", "=", card.id)]
    SudoSaleOrderCouponPoints = env["sale.order.coupon.points"].sudo()
    count = SudoSaleOrderCouponPoints.search_count(domain)

    history = SudoSaleOrderCouponPoints.search(
        domain, limit=paging_.limit, offset=paging_.offset
    )
    return PagedCollection(
        items=[LoyaltyCardHistory.from_sale_order_coupon_point(rec) for rec in history],
        count=count,
    )
