# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import SaleWithQtyUnavailableDiff

carts_router = APIRouter(tags=["carts"])


@carts_router.post("/carts/refresh_qty_unavailable")
@carts_router.post("/carts/{uuid}/refresh_qty_unavailable")
def refresh_qty_unavailable(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    uuid: str | None = None,
) -> SaleWithQtyUnavailableDiff:
    """This service refresh the qty_unavailable info on the cart lines.

    As result, a new field 'qty_unavailable_diff' is added into the line
    info. This field is filled with the delta qty of unavailable product
    before and after the recompute of unavailable product for the given line.
    The new qty is applied to the line and a new call to the method
    will give 0 as qty_unavailable_diff if there is no diff between 2 calls
    """
    cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    if not cart:
        raise HTTPException(status_code=404, detail="No cart found")
    if uuid and cart.uuid != uuid:
        raise HTTPException(status_code=404, detail="No cart found")
    updated_lines = cart.refresh_product_qties_unavailable()
    return SaleWithQtyUnavailableDiff.from_sale_order(cart, updated_lines)
