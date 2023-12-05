# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import functools
import logging
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError, ResponseValidationError

from odoo import api, fields

from odoo.addons.fastapi.dependencies import (
    authenticated_partner_impl as authenticated_partner_impl_base,
)
from odoo.addons.fastapi.models.fastapi_endpoint import (
    FastapiEndpoint as FastapiEndpointBase,
)

from ..dependencies import authenticated_partner_impl
from ..routers.products import router as products_router
from ..routers.recipients import router as recipients_router
from ..routers.sales import router as sales_router
from ..routers.stocks import router as stocks_router
from .alc_b2c_client import AlcB2cClient

_logger = logging.getLogger(__name__)


class FastapiEndpoint(FastapiEndpointBase):

    app: str = fields.Selection(
        selection_add=[("b2c", "B2C")], ondelete={"b2c": "cascade"}
    )
    client_ids = fields.One2many[AlcB2cClient](
        inverse_name="fastapi_endpoint_id", string="Clients"
    )

    @api.model
    def _get_fastapi_routers(self):
        if self.app == "b2c":
            return [products_router, recipients_router, sales_router, stocks_router]
        return super()._get_fastapi_routers()

    def _get_app(self):
        app = super()._get_app()
        if self.app == "b2c":
            app.dependency_overrides[
                authenticated_partner_impl_base
            ] = authenticated_partner_impl
        return app

    def _get_app_exception_handlers(
        self,
    ) -> dict[
        int | type[Exception],
        Callable[[Request, Exception], Response | Awaitable[Response]],
    ]:
        handlers = super()._get_app_exception_handlers()
        new_handlers = {}
        if self.app == "b2c":
            for exception, handler in handlers.items():
                # we will wrap the handler to log the exception in any case
                async def wrapped_handler(request, exc, handle):
                    _logger.info(
                        "Exception while handling request %s", str(exc), exc_info=exc
                    )
                    return await handle(request, exc)

                new_handlers[exception] = functools.partial(
                    wrapped_handler, handle=handler
                )
            new_handlers[RequestValidationError] = validation_exception_handler
            new_handlers[ResponseValidationError] = validation_exception_handler
        return new_handlers


async def validation_exception_handler(request, exc):
    _logger.info("The client sent invalid data!: %s", exc.errors())
    return await request_validation_exception_handler(request, exc)
