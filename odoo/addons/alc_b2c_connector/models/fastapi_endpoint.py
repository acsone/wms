# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


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
