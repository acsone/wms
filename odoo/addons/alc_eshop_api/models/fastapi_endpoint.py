# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import partial
from typing import Any

from fastapi import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer
from starlette.datastructures import URL
from starlette.middleware import Middleware
from starlette.types import ASGIApp, Receive, Scope, Send

from odoo import api, fields

from odoo.addons.alc_eshop_api_cart.routers import carts_router
from odoo.addons.alc_eshop_api_cart_delivery.routers import (
    carts_router as carts_router_delivery,
)
from odoo.addons.alc_eshop_api_cart_product_unavailable.routers import (
    carts_router as carts_router_product_unavailable,
)
from odoo.addons.alc_eshop_api_catalog.routers import brands_router, catalog_router
from odoo.addons.alc_eshop_api_classifieds.routers import classified_ads_router
from odoo.addons.alc_eshop_api_cms.routers import cms_router
from odoo.addons.alc_eshop_api_customer.routers import customer_router
from odoo.addons.alc_eshop_api_delivery_carriers.routers import delivery_carriers_router
from odoo.addons.alc_eshop_api_discounts.routers import discounts_router
from odoo.addons.alc_eshop_api_documents.routers import documents_router
from odoo.addons.alc_eshop_api_forms.routers import forms_router
from odoo.addons.alc_eshop_api_orders.routers import orders_router
from odoo.addons.alc_eshop_api_pickings.routers import pickings_router
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
from odoo.addons.shopinvader_api_sale.routers.sales import sale_router
from odoo.addons.shopinvader_api_wishlist.routers import wishlist_router


class FastapiEndpoint(FastapiEndpointBase):

    app: str = fields.Selection(
        selection_add=[("alc_eshop_app", "Alcyon EShop Endpoint")],
        ondelete={"alc_eshop_app": "cascade"},
    )
    auth_jwt_validator_id = fields.Many2one[AuthJwtValidator]()

    oauth_host = fields.Char(default="https://account.test.alcyon.acsone.eu")
    oauth_realm_name = fields.Char(default="alcyon")
    oauth_client_id = fields.Char(default="shopinvader")

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
            orders_router,
            pickings_router,
            customer_router,
            carts_router,
            carts_router_product_unavailable,
            sale_router,
            wishlist_router,
            delivery_carriers_router,
            carts_router_delivery,
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
        tags_metadata.append(
            {
                "name": "orders",
                "description": "List the partner's orders",
            }
        )
        return tags_metadata

    def _prepare_fastapi_app_params(self) -> dict[str, Any]:
        params = super()._prepare_fastapi_app_params()
        if self.app == "alc_eshop_app":
            params["openapi_tags"] = self._get_alc_eshop_app_tags(params)
            params["swagger_ui_oauth2_redirect_url"] = "/docs/oauth2-redirect"
            params["swagger_ui_init_oauth"] = {
                "clientId": self.oauth_client_id,
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
                    f"{self.oauth_host}/auth/realms/{self.oauth_realm_name}/protocol/openid-connect/auth"
                ),
                tokenUrl=(
                    f"{self.oauth_host}/auth/realms/{self.oauth_realm_name}/protocol/openid-connect/token"
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
            middlewares.extend(
                [
                    Middleware(
                        RedirectMiddleware,
                        root_path=self.root_path,
                        old_path="/v2/cart",
                        new_path="/carts",
                    ),
                    Middleware(
                        RedirectMiddleware,
                        root_path=self.root_path,
                        old_path="/wishlist",
                        new_path="/wishlists",
                    ),
                ]
            )
        return middlewares


class RedirectMiddleware:
    def __init__(self, app: ASGIApp, root_path: str, old_path: str, new_path) -> None:
        self.app = app
        self.root_path = root_path
        self.old_path = old_path
        self.new_path = new_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http"):
            url = URL(scope=scope)
            if url.path.startswith(
                f"{self.root_path}{self.old_path}"
            ) and not url.path.startswith(f"{self.root_path}{self.new_path}"):
                scope["path"] = scope["path"].replace(self.old_path, self.new_path)
        await self.app(scope, receive, send)
