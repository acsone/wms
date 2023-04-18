# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import APIRouter, Depends, HTTPException, status

from odoo import api, fields
from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.depends import (
    authenticated_partner_impl,
    fastapi_endpoint,
    odoo_env,
)
from odoo.addons.fastapi.models.fastapi_endpoint import (
    FastapiEndpoint as FastapiEndpointBase,
)

from ..utils import api_key_header
from .fastapi_endpoint_settings import FastapiEndpointSettings


class FastapiEndpoint(FastapiEndpointBase):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("b2c", "B2C")], ondelete={"b2c": "cascade"}
    )
    setting_ids = fields.One2many[FastapiEndpointSettings](
        inverse_name="fastapi_endpoint_id", string="Settings"
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
                authenticated_partner_impl
            ] = fastapi_endpoint_setting_based_authenticated_partner_impl
        return app


def fastapi_endpoint_setting_based_authenticated_partner_impl(
    api_key: str = Depends(api_key_header),  # noqa: B008
    env: Environment = Depends(odoo_env),  # noqa: B008
    endpoint: FastapiEndpoint = Depends(fastapi_endpoint),  # noqa: B008
) -> Partner:
    """A dummy implementation that look for a user with the same login.

    as the provided api key
    """
    setting = (
        env["fastapi.endpoint.settings"]
        .sudo()
        .search(
            [
                ("fastapi_endpoint_id", "=", endpoint.id),
                ("auth_api_key_id.key", "=", api_key),
            ]
        )
    )
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key"
        )
    return setting.auth_api_key_id.user_id.partner_id


b2c_api_router = APIRouter(
    dependencies=[Depends(fastapi_endpoint_setting_based_authenticated_partner_impl)]
)
