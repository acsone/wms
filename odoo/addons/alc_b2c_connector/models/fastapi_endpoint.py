# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.api import Environment

from odoo.addons.fastapi.depends import (
    authenticated_partner_impl as authenticated_partner_impl_base,
    fastapi_endpoint,
    odoo_env,
)
from odoo.addons.fastapi.models.fastapi_endpoint import (
    FastapiEndpoint as FastapiEndpointBase,
)

from fastapi import APIRouter, Depends, HTTPException, status

from ..models.res_partner import ResPartner
from ..services.utils import api_key_header
from .alc_b2c_client import AlcB2cClient


class FastapiEndpoint(FastapiEndpointBase):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("b2c", "B2C")], ondelete={"b2c": "cascade"}
    )
    client_ids = fields.One2many[AlcB2cClient](
        inverse_name="fastapi_endpoint_id", string="Clients"
    )

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "b2c":
            return [b2c_api_router]
        return super()._get_fastapi_routers()

    def _get_app(self):
        app = super()._get_app()
        if self.app == "b2c":
            app.dependency_overrides[
                authenticated_partner_impl_base
            ] = authenticated_partner_impl
        return app


def __alc_b2c_client_base(
    api_key: str = Depends(api_key_header),  # noqa: B008
    env: Environment = Depends(odoo_env),  # noqa: B008
    endpoint: FastapiEndpoint = Depends(fastapi_endpoint),  # noqa: B008
) -> AlcB2cClient:
    """Return the fastapi.endpoint record."""
    return env["alc.b2c.client"].search(
        [("fastapi_endpoint_id", "=", endpoint.id), ("api_key", "=", api_key)]
    )


def authenticated_partner_impl(
    client: AlcB2cClient = Depends(__alc_b2c_client_base),  # noqa: B008
) -> ResPartner:
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key"
        )
    return client.partner_id.with_context(alc_b2c_client_id=client.id)


b2c_api_router = APIRouter(dependencies=[Depends(authenticated_partner_impl)])
