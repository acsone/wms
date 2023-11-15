# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import CartUpdateRequest

carts_router = APIRouter(tags=["carts"])


@carts_router.post("/carts/info")
@carts_router.post("/carts/{uuid}/info")
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
        upd_vals = cart_info.to_sale_order_vals()
        if upd_vals:
            cart.write(upd_vals)
    return Sale.from_sale_order(cart)


@carts_router.post("/carts/confirm")
@carts_router.post("/carts/{uuid}/confirm")
def confirm(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    cart_info: CartUpdateRequest,
    uuid: str | None = None,
) -> Sale:
    params = cart_info.model_dump(exclude_unset=True)
    uuid = uuid or params.get("uuid")
    cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    if not cart:
        return HTTPException(status_code=404, detail="Not cart found")
    if uuid and cart.uuid != uuid:
        return HTTPException(status_code=404, detail="Not cart found")
    if not cart.partner_id.eshop_ordering_allowed:
        raise ValidationError(_("You are no allowed to pass an order on the EShop"))
    upd_vals = cart_info.to_sale_order_vals()
    upd_vals["date_order"] = fields.Datetime.now()
    upd_vals.update(cart.play_onchanges(upd_vals, upd_vals.keys()))
    if upd_vals:
        cart.update(upd_vals)
    cart.action_confirm_cart()
    cart._notify_note()
    cart.action_confirm()
    return Sale.from_sale_order(cart)
