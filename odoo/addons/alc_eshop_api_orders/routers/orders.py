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

from ..schemas import Order, OrderList, SaleChannel

orders_router = APIRouter(tags=["orders"])


@orders_router.get("/orders")
def search(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    from_date: datetime | None = None,
    sale_channel: SaleChannel | None = None,
    page: Annotated[
        int | None,
        Query(
            description="Page number\n"
            "Replaces the 'limit' parameter which is deprecated",
            validation_alias=AliasChoices("page", "limit"),
        ),
    ] = 1,
    per_page: int | None = 10,
) -> OrderList:
    domain = [("partner_id", "=", partner.id), ("typology", "=", "sale")]
    if from_date:
        from_date = from_date.astimezone(pytz.timezone("UTC"))
        domain.append(("create_date", ">=", from_date))
    if sale_channel:
        channel_id = env["sale.channel"].sudo()._get_id_from_code(sale_channel.value)
        domain.append(("sale_channel_id", "=", channel_id))
    else:
        domain.append(
            ("sale_channel_id", "in", env["sale.channel"].sudo()._get_internal_ids())
        )
    model = env["sale.order"].sudo()
    total_count = model.search_count(domain)
    offset = per_page * (page - 1)
    order = "date_order desc, name desc"
    records = model.search(domain, limit=per_page, offset=offset, order=order)
    return OrderList(
        data=[Order.from_sale_order(record) for record in records],
        size=total_count,
    )
