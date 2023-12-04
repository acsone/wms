# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import Depends, HTTPException, Query, Request, status
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
    offset: Annotated[str | int | None, Query()] = 0,
    limit: Annotated[str | int | None, Query()] = 80,
) -> Paging:
    """Return a Paging object from the page and page_size parameters."""
    if isinstance(offset, str) and offset.isdigit():
        offset = int(offset)
    if isinstance(limit, str) and limit.isdigit():
        limit = int(limit)
    limit = limit or 80
    offset = offset or 0
    return Paging(limit=limit, offset=offset)


def sku_list(
    request: Request,
    skus: Annotated[str | list[str] | None, Query()] = None,
) -> list[str]:
    """Return a list of SKUs from the skus parameter."""
    if not skus:
        skus = _deep_parse_query_request_for_list("skus", request)
    return skus


def ids_list(
    request: Request,
    ids: Annotated[str | list[str] | None, Query()] = None,
) -> list[str]:
    """Return a list of IDs from the ids parameter."""
    if not ids:
        ids = _deep_parse_query_request_for_list("ids", request)
    return ids


def _deep_parse_query_request_for_list(key: str, request: Request) -> list[str]:
    """Try to get a list of values from the request query parameters.

    Whatever the way the list is provided (array syntax, multiple values,
    array item representation), this function will try to find it and
    return it as a list of string.

    This function is here to help maintain compatibility with the previous
    version of the API where the list of values was provided as
    array syntax (e.g. ids[]=1&ids[]=2 or ids[0]=1&ids[0]=2).
    """
    # the key parameter could have been provided as individual query
    # parameter with array syntax, or as a single query parameter with
    # multiple values, or array item representation (e.g. ids[0]=1&ids[1]=2)
    values = request.query_params.getlist(f"{key}[]")
    if not values:
        values = request.query_params.getlist(key)
    if not values:
        for param, value in request.query_params.multi_items():
            if param.startswith(f"{key}["):
                values.append(value)
    return values
