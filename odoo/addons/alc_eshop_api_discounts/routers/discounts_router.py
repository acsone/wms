# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import Discount, DiscountList

discounts_router = APIRouter(tags=["discounts"])


@discounts_router.get("/discounts", status_code=200)
def get(
    partner: Annotated[Partner, Depends(authenticated_partner)],
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    limit: int | None = 10,
    page: int = 1,
    reference: Annotated[
        str | None,
        Query(descripton="The product reference you search the discount for"),
    ] = None,
    reference__ilike: Annotated[
        str | None,
        Query(descripton="Part of the product reference you search the discount for"),
    ] = None,
) -> DiscountList:
    if not partner.supplier_promotion_sale_allowed:
        domain = [(0, "=", 1)]
    else:
        domain = partner._get_product_domain()
        if partner.partner_type != "veterinary":
            domain.append(["only_for_veterinaries", "=", False])
        domain[0] = ("product_tmpl_id." + domain[0][0], domain[0][1], domain[0][2])
        domain.append(("is_past", "=", False))
    if reference:
        domain.append(("product_tmpl_id.default_code", "=", reference))
    if reference__ilike:
        domain.append(("product_tmpl_id.default_code", "ilike", reference__ilike))
    offset = limit * (page - 1) if limit and page else 0
    model = env["product.supplierinfo"].sudo()
    records = model.search(domain, limit=limit, offset=offset)
    count = model.search_count(domain)
    return DiscountList(
        data=[Discount.from_product_supplierinfo(record) for record in records],
        size=count,
    )
