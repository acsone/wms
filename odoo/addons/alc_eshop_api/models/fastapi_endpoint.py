# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import partial
from typing import Any

from fastapi import APIRouter, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.types import ASGIApp

from odoo import api, fields

from odoo.addons.alc_eshop_api_catalog.routers import brands_router, catalog_router
from odoo.addons.alc_eshop_api_classifieds.routers import classified_ads_router
from odoo.addons.alc_eshop_api_cms.routers import cms_router
from odoo.addons.alc_eshop_api_discounts.routers import discounts_router
from odoo.addons.alc_eshop_api_documents.routers import documents_router
from odoo.addons.alc_eshop_api_forms.routers import forms_router
from odoo.addons.alc_eshop_api_products_on_order.routers import products_on_order_router
from odoo.addons.alc_eshop_api_promotion_subscriptions.routers import (
    promo_subscriptions_router,
)
from odoo.addons.alc_eshop_api_registration.routers import registrations_router
from odoo.addons.alc_eshop_api_sale_statistic.routers import sale_statistics_router
from odoo.addons.alc_eshop_api_veterinary_groups.routers import veterinary_groups_router
from odoo.addons.auth_jwt.models.auth_jwt_validator import AuthJwtValidator
from odoo.addons.fastapi.dependencies import (
    authenticated_partner_impl,
    optionally_authenticated_partner_impl,
)
from odoo.addons.fastapi.models.fastapi_endpoint import (
    FastapiEndpoint as FastapiEndpointBase,
)
from odoo.addons.fastapi_auth_jwt.dependencies import (
    auth_jwt_authenticated_partner,
    auth_jwt_default_validator_name,
    auth_jwt_http_header_authorization,
    auth_jwt_optionally_authenticated_partner,
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
            classified_ads_router,
            cms_router,
            sale_statistics_router,
            registrations_router,
            documents_router,
            brands_router,
            catalog_router,
            discounts_router,
            products_on_order_router,
            veterinary_groups_router,
            promo_subscriptions_router,
            forms_router,
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
                "description": "Set of services to manage carts. Previously, cart "
                "services were available under /v2/cart. They are now available "
                "under /carts. The /v2/cart endpoint is still available but "
                "is deprecated and internally redirect to /carts.",
            }
        )
        tags_metadata.append(
            {
                "name": "classified_ads",
                "description": "Set of services to manage classified advertisements",
            }
        )
        tags_metadata.append(
            {
                "name": "cms",
                "description": "Set of services to manage cms content",
            }
        )
        tags_metadata.append(
            {
                "name": "registrations",
                "description": "Set of services to manage registrations",
            }
        )
        tags_metadata.append(
            {
                "name": "documents",
                "description": "Set of services to get access to the partner's "
                "documents",
            }
        )
        tags_metadata.append(
            {
                "name": "brands",
                "description": "Set of services to get access to the product's "
                "brands",
            }
        )
        tags_metadata.append(
            {
                "name": "catalog",
                "description": "Set of services to get access to the product's "
                "catalog available for the partner catalog",
            }
        )
        tags_metadata.append(
            {
                "name": "discounts",
                "description": "Set of services to get access to the product's "
                "discounts available for the partner",
            }
        )
        tags_metadata.append(
            {
                "name": "products_on_order",
                "description": "Set of services to get access to the product's "
                "on order for the logged partner. It also provides the possibility "
                "to cancel a product on order.",
            }
        )
        tags_metadata.append(
            {
                "name": "veterinary_groups",
                "description": "Service to get access to the partner's "
                "veterinary groups informations",
            }
        )
        tags_metadata.append(
            {
                "name": "promo_subscriptions",
                "description": "Set of services to manage subscriptions on "
                "product promotions",
            }
        )
        tags_metadata.append(
            {
                "name": "forms",
                "description": "Set of services to manage forms",
            }
        )
        return tags_metadata

    def _prepare_fastapi_app_params(self) -> dict[str, Any]:
        params = super()._prepare_fastapi_app_params()
        if self.app == "alc_eshop_app":
            params["openapi_tags"] = self._get_alc_eshop_app_tags(params)
            params["swagger_ui_oauth2_redirect_url"] = "/docs/oauth2-redirect"
            params["swagger_ui_init_oauth"] = {
                "clientId": "demo16.shopinvader.com",
            }
            params["swagger_ui_parameters"] = {
                "docExpansion": "none",
                "filter": True,
                "tagsSorter": "alpha",
            }
        return params

    def _get_app(self):
        app = super()._get_app()
        if self.app == "alc_eshop_app":
            app.include_router(router=cart_router, prefix="/carts")
        return app

    def _get_app_dependencies_overrides(self):
        overrides = super()._get_app_dependencies_overrides()
        if self.app == "alc_eshop_app":
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
            overrides.update(
                {
                    authenticated_partner_impl: auth_jwt_authenticated_partner,
                    auth_jwt_default_validator_name: partial(
                        lambda a: a, self.auth_jwt_validator_id.name or None
                    ),
                    auth_jwt_http_header_authorization: oauth2_scheme,
                    optionally_authenticated_partner_impl: auth_jwt_optionally_authenticated_partner,
                }
            )
        return overrides

    def _get_fastapi_app_middlewares(self) -> list[Middleware]:
        middlewares = super()._get_fastapi_app_middlewares()
        if self.app == "alc_eshop_app":
            middlewares.append(
                Middleware(RedirectV2CartMiddleware, root_path=self.root_path)
            )
        return middlewares


class RedirectV2CartMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
        root_path: str = "",
    ) -> None:
        super().__init__(app, dispatch)
        self.root_path = root_path

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(f"{self.root_path}/v2/cart"):
            request.scope["path"] = request.scope["path"].replace("/v2/cart", "/carts")
        return await call_next(request)
