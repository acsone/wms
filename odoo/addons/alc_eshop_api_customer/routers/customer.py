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

from ..schemas import CustomerData, CustomerUpdate, SalesPerson

customer_router = APIRouter(tags=["customer"])


@customer_router.get("/customer")
def get_info(
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> CustomerData:
    """Get the customer info."""
    return CustomerData.from_res_partner(partner)


@customer_router.get("/customer/sales_person")
def get_sales_person(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> SalesPerson:
    """Get the customer sales person."""
    partner = partner.user_id.partner_id or env.company.partner_id
    return SalesPerson.from_res_partner(partner)


@customer_router.put("/customer")
def update_info(
    data: CustomerUpdate,
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> CustomerData:
    """Update the customer info."""
    partner.write(data.to_res_partner())
    return CustomerData.from_res_partner(partner)
