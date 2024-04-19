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

from ..schemas import DeliveryMethodList

delivery_carriers_router = APIRouter(tags=["delivery_carriers"])


@delivery_carriers_router.get("/delivery_carriers/", deprecated=True)
@delivery_carriers_router.get("/delivery_carriers", deprecated=True)
@delivery_carriers_router.get("/delivery_methods")
@delivery_carriers_router.get("/delivery_methods/", deprecated=True)
def search(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    cart_uuid: str | None = None,
) -> DeliveryMethodList:
    """Get all delivery carriers."""
    cart = env["sale.order"]._find_open_cart(partner.id, cart_uuid)
    if not cart:
        raise HTTPException(status_code=404, detail="Car not found")
    carriers = cart._get_available_carriers()
    return DeliveryMethodList.from_delivery_carrier(carriers)
