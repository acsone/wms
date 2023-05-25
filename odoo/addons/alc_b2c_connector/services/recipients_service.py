# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env

from ..models.fastapi_endpoint import b2c_api_router
from .depends import AlcB2cClient, alc_b2c_client
from .models.partner import PartnerRequest, PartnerResponse


@b2c_api_router.get("/recipients/{id}", response_model=PartnerResponse)
@b2c_api_router.get("/recipients/{id}/get", response_model=PartnerResponse)
@b2c_api_router.post("/recipients/{id}", response_model=PartnerResponse)
@b2c_api_router.put("/recipients/{id}", response_model=PartnerResponse)
def _get_partners(
    id: str,  # pylint: disable=redefined-builtin
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008
) -> PartnerResponse:
    """Get partner by id."""
    b2c_ref = env["res.partner"]._b2c_id_to_b2c_ref(id, client)
    partner = env["res.partner"]._get_partner_by_ref(b2c_ref)
    return PartnerResponse.from_orm(partner)


@b2c_api_router.post("/recipients/{id}/update", response_model=PartnerResponse)
def _update_partner(
    id: str,  # pylint: disable=redefined-builtin
    body: PartnerRequest,
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
    client: AlcB2cClient = Depends(alc_b2c_client),  # noqa: B008,
) -> PartnerResponse:
    """Update partner."""
    partner = env["res.partner"]._update_b2c_recipient(
        id, client, body._convert_to_write()
    )
    return PartnerResponse.from_orm(partner)
