# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class BaseShopinvaderService(AbstractComponent):
    _inherit = "base.shopinvader.service"

    def _get_openapi_default_parameters(self):
        defaults = super(BaseShopinvaderService, self)._get_openapi_default_parameters()
        for default in defaults:
            if default["name"] == "PARTNER-EMAIL":
                default.update(
                    {
                        "name": "PARTNER-IDENTITY",
                        "description": "Partner identity: The partner identity is "
                        "the concatenation of the partner reference and the partner "
                        "login into the alcyon website separated by a pipe character. "
                        "Example: 123456789|john.doe. This field is required when "
                        "authenticated by auth_api_key.",
                        "required": True,
                    }
                )
        return defaults
