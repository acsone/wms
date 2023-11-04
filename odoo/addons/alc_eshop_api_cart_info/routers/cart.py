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
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import CartUpdateRequest

carts_router = APIRouter(tags=["carts"])


@carts_router.post("/carts/info", status_code=205)
@carts_router.post("/carts/{uuid}/info", status_code=205)
def update_cart_info(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    cart_info: CartUpdateRequest,
    uuid: str | None = None,
) -> Sale:
    """Update cart info."""
    params = cart_info.model_dump(exclude_unset=True)
    uuid = uuid or params.get("uuid")
    cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    if not cart:
        cart = env["sale.order"]._create_empty_cart(partner.id)
    if not uuid or cart.uuid == uuid:
        # update only if the cart is the one requested
        upd_vals = {}
        customer_ref = params.get("customer_ref")
        if customer_ref:
            upd_vals["client_order_ref"] = customer_ref
        note = params.get("note")
        if note:
            upd_vals["note"] = note
        if upd_vals:
            cart.write(upd_vals)
    return Sale.from_sale_order(cart)
