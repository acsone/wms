# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, Query
from pydantic import AliasChoices

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import Picking, PickingList

pickings_router = APIRouter(tags=["pickings"])


@pickings_router.get("/pickings")
def get_all(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    from_date: datetime | None = None,
    page: Annotated[
        int | None,
        Query(
            description="Page number\n"
            "Replaces the 'limit' parameter which is deprecated",
            validation_alias=AliasChoices("page", "limit"),
        ),
    ] = 1,
    per_page: int | None = 10,
) -> PickingList:
    """Get all pickings."""
    return _search(env, partner, page, per_page, from_date=from_date)


@pickings_router.get("/pickings/canceled")
def get_canceled(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    from_date: datetime | None = None,
    page: Annotated[
        int | None,
        Query(
            description="Page number\n"
            "Replaces the 'limit' parameter which is deprecated",
            validation_alias=AliasChoices("page", "limit"),
        ),
    ] = 1,
    per_page: int | None = 10,
) -> PickingList:
    """Get canceled pickings."""
    states = ["cancel"]
    return _search(
        env, partner, page, per_page, states=states, from_date=from_date, canceled=True
    )


@pickings_router.get("/pickings/done")
def get_done(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    from_date: datetime | None = None,
    page: Annotated[
        int | None,
        Query(
            description="Page number\n"
            "Replaces the 'limit' parameter which is deprecated",
            validation_alias=AliasChoices("page", "limit"),
        ),
    ] = 1,
    per_page: int | None = 10,
) -> PickingList:
    """Get completed pickings."""
    states = ["done"]
    return _search(env, partner, page, per_page, states=states, from_date=from_date)


def _search(
    env: api.Environment,
    partner: Partner,
    page: int | None,
    per_page: int | None,
    states: list[str] = None,
    from_date: datetime | None = None,
    canceled: bool = False,
) -> PickingList:
    lid = env.ref("stock.stock_location_customers").id
    domain = [
        # the final client should not be a B2C customer it should be the VT
        # that's why we search on the customer_id and not on the partner_id
        # which is the delivery address
        ("customer_id", "child_of", partner.id),
        ("location_dest_id", "=", lid),
    ]
    if from_date:
        from_date = from_date.astimezone(pytz.timezone("UTC"))
        date_key = "date_done" if states == ["done"] else "create_date"
        domain += [(date_key, ">=", from_date)]
    if states and not canceled:
        domain += [("state", "in", states)]
    if canceled:
        domain += ["|", ("state", "=", "cancel"), ("move_ids.state", "=", "cancel")]
    model = env["stock.picking"].sudo()
    total_count = model.search_count(domain)
    offset = per_page * (page - 1) if per_page and page else 0
    records = model.search(domain, limit=per_page, offset=offset)
    return PickingList(
        data=[Picking.from_stock_picking(record) for record in records],
        size=total_count,
    )
