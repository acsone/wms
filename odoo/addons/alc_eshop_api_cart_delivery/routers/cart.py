# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from odoo import _, api
from odoo.exceptions import UserError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.shopinvader_schema_sale.schemas import Sale

from ..schemas import SetDeliveryMethodRequest

carts_router = APIRouter(tags=["carts"])


@carts_router.post("/carts/set_delivery_method")
@carts_router.post("/carts/{uuid}/set_delivery_method")
def set_delivery_method(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    rqst: SetDeliveryMethodRequest,
    uuid: str | None = None,
) -> Sale:
    """This service will set the given delivery method to the current.

    cart
    """
    cart = env["sale.order"]._find_open_cart(partner.id, uuid)
    if not cart:
        raise HTTPException(status_code=404, detail="No cart found")
    if uuid and cart.uuid != uuid:
        raise HTTPException(status_code=404, detail="No cart found")
    carrier_id = env["delivery.carrier"].search(
        [("id", "=", rqst.method_id), ("available_in_website", "=", True)]
    )
    if not carrier_id:
        raise HTTPException(status_code=404, detail="Not delivery method found")
    if not cart._is_delivery_method_available(rqst.method_id):
        raise UserError(_("This delivery method is not available for your order"))

    cart.carrier_id = carrier_id
    return Sale.from_sale_order(cart)
