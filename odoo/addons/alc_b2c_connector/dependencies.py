# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import APIKeyHeader

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import (
    authenticated_partner_env,
    fastapi_endpoint,
    odoo_env,
)
from odoo.addons.fastapi.models import FastapiEndpoint
from odoo.addons.fastapi.schemas import Paging

from .models.alc_b2c_client import AlcB2cClient
from .models.res_partner import ResPartner

api_key_header = APIKeyHeader(
    name="api-key",
    description="In this demo, you can use a user's login as api key.",
)


def _alc_b2c_client_id(
    api_key: Annotated[str, Depends(api_key_header)],
    env: Annotated[Environment, Depends(odoo_env)],
    endpoint: Annotated[FastapiEndpoint, Depends(fastapi_endpoint)],
) -> int:
    """Return the fastapi.endpoint record."""
    return env["alc.b2c.client"]._get_id_by_endpoint_id_and_api_key(
        endpoint.id, api_key
    )


def alc_b2c_client(
    client_id: Annotated[int, Depends(_alc_b2c_client_id)],
    env: Annotated[Environment, Depends(authenticated_partner_env)],
) -> AlcB2cClient:
    return env["alc.b2c.client"].browse(client_id)


def authenticated_partner_impl(
    client_id: Annotated[int, Depends(_alc_b2c_client_id)],
    env: Annotated[Environment, Depends(odoo_env)],
) -> ResPartner:
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key"
        )
    client = env["alc.b2c.client"].browse(client_id)
    return client.partner_id.with_context(alc_b2c_client_id=client.id)


def paging(
    offset: Annotated[int | None, Query(gte=1)] = 0,
    limit: Annotated[int | None, Query(gte=1)] = 80,
) -> Paging:
    """Return a Paging object from the page and page_size parameters."""
    return Paging(limit=limit, offset=offset)
