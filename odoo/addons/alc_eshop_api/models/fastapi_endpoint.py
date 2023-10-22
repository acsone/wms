# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import partial
from typing import Any

from fastapi import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer

from odoo import api, fields

from odoo.addons.alc_eshop_api_classifieds.routers import classified_ads_router
from odoo.addons.alc_eshop_api_sale_statistic.routers import sale_statistics_router
from odoo.addons.auth_jwt.models.auth_jwt_validator import AuthJwtValidator
from odoo.addons.fastapi.dependencies import authenticated_partner_impl
from odoo.addons.fastapi.models.fastapi_endpoint import (
    FastapiEndpoint as FastapiEndpointBase,
)
from odoo.addons.fastapi_auth_jwt.dependencies import (
    auth_jwt_authenticated_partner,
    auth_jwt_default_validator_name,
    auth_jwt_http_header_authorization,
)
from odoo.addons.shopinvader_api_address.routers.address_service import address_router
from odoo.addons.shopinvader_api_cart.routers import cart_router


class FastapiEndpoint(FastapiEndpointBase):

    app: str = fields.Selection(
        selection_add=[("alc_eshop_app", "Alcyon EShop Endpoint")],
        ondelete={"alc_eshop_app": "cascade"},
    )
    auth_jwt_validator_id = fields.Many2one[AuthJwtValidator]()

    def _get_fastapi_routers(self):
        if self.app == "alc_eshop_app":
            return self._get_alc_eshop_app_fastapi_routers()
        return super()._get_fastapi_routers()

    @api.model
    def _get_alc_eshop_app_fastapi_routers(self) -> list[APIRouter]:
        if "address" not in address_router.tags:
            address_router.tags.append("address")
        return [
            address_router,
            cart_router,
            sale_statistics_router,
            classified_ads_router,
        ]

    def _get_alc_eshop_app_tags(self, params) -> list:
        tags_metadata = params.get("openapi_tags", []) or []
        tags_metadata.append(
            {
                "name": "addresses",
                "description": "Set of services to manage addresses",
            }
        )
        tags_metadata.append(
            {
                "name": "sale_statistics",
                "description": "Set of services to manage sale statistics",
            }
        )
        self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        tags_metadata.append(
            {
                "name": "carts",
                "description": "Set of services to manage carts",
            }
        )
        tags_metadata.append(
            {
                "name": "classified_ads",
                "description": "Set of services to manage classified advertisements",
            }
        )
        return tags_metadata

    def _prepare_fastapi_app_params(self) -> dict[str, Any]:
        params = super()._prepare_fastapi_app_params()
        if self.app == "alc_eshop_app":
            params["openapi_tags"] = self._get_alc_eshop_app_tags(params)
            params[
                "swagger_ui_oauth2_redirect_url"
            ] = "/alc_eshop_app/docs/oauth2-redirect"
            params["swagger_ui_init_oauth"] = {
                "clientId": "demo16.shopinvader.com",
            }
        return params

    def _get_alc_eshop_app_app_dependencies_overrides(self):
        oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl=(
                "https://keycloak.demo16.shopinvader.com/"
                "auth/realms/master/protocol/openid-connect/auth"
            ),
            tokenUrl=(
                "https://keycloak.demo16.shopinvader.com/"
                "auth/realms/master/protocol/openid-connect/token"
            ),
            scopes={"openid": "", "email": "", "profile": ""},
            # Don't fail if missing Authorization header, as we look for the cookie too.
            auto_error=False,
        )
        return {
            authenticated_partner_impl: auth_jwt_authenticated_partner,
            auth_jwt_default_validator_name: partial(
                lambda a: a, self.auth_jwt_validator_id.name or None
            ),
            auth_jwt_http_header_authorization: oauth2_scheme,
        }
