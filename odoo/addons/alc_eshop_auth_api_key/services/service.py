# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class BaseRestService(AbstractComponent):
    _inherit = "base.rest.service"

    def _get_openapi_default_parameters(self):
        defaults = super()._get_openapi_default_parameters()
        if self._collection in ("shopinvader.backend", "shopinvader.api.v2"):
            defaults.append(
                {
                    "name": "PARTNER-IDENTITY",
                    "description": "Partner identity: The partner identity is "
                    "the concatenation of the partner reference and the partner "
                    "login into the alcyon website separated by a pipe character. "
                    "Example: 123456789|john.doe. This field is required when "
                    "authenticated by auth_api_key.",
                    "required": False,
                    "schema": {"type": "string"},
                    "style": "simple",
                    "in": "header",
                }
            )
        return defaults


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def _get_openapi_default_parameters(self):
        defaults = super()._get_openapi_default_parameters()
        if self._collection in ("shopinvader.backend", "shopinvader.api.v2"):
            defaults = [d for d in defaults if d["name"] != "PARTNER-EMAIL"]
        return defaults
