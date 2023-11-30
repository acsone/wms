# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env

from ..dependencies import AlcB2cClient, alc_b2c_client
from ..schemas.partner import PartnerRequest, PartnerResponse

router = APIRouter(tags=["recipients"])


@router.get("/recipients/{id}")
@router.get("/recipients/{id}/get")
def _get_partners(
    id: str,  # pylint: disable=redefined-builtin
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
) -> PartnerResponse:
    """Get partner by id."""
    b2c_ref = env["res.partner"]._b2c_id_to_b2c_ref(id, client)
    partner = env["res.partner"]._get_partner_by_ref(b2c_ref)
    return PartnerResponse.from_res_partner(partner)


@router.post("/recipients/{id}/update")
@router.post("/recipients/{id}")
@router.put("/recipients/{id}")
def _update_partner(
    id: str,  # pylint: disable=redefined-builtin
    body: PartnerRequest,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
    client: Annotated[AlcB2cClient, Depends(alc_b2c_client)],
) -> PartnerResponse:
    """Update partner."""
    partner = env["res.partner"]._update_b2c_recipient(
        id, client, body._convert_to_write()
    )
    return PartnerResponse.from_res_partner(partner)
