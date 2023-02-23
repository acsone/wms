# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ShopinvaderAuthApiKeyServiceContextProvider(Component):
    _inherit = "auth_api_key.shopinvader.service.context.provider"

    def _get_shopinvader_partner(self):
        # disable useless shopinvader partner
        return self.env["shopinvader.partner"].browse()

    def _get_authenticated_partner_id(self):
        return self._get_authenticated_partner().id

    def _get_authenticated_partner(self):
        headers = self.request.httprequest.environ
        partner_identity = headers.get("HTTP_PARTNER_IDENTITY")
        # The partner identity is the concatenation of the partner reference
        # and the partner login into the alcyon webside separated by a pipe
        # character.
        # Example: 123456789|john.doe
        if not partner_identity:
            raise MissingError(_("Partner identity is missing into the header!"))

        partner_reference, partner_login = partner_identity.split("|")
        if not partner_reference or not partner_login:
            _logger.warning(
                "Wrong HTTP_PARTNER_IDENTITY, header ignored: %s", partner_identity
            )
            raise MissingError(_("The given identity is not well formatted!"))
        keycloak_user = self.env["keycloak.user"].search(
            [("keycloak_username", "=", partner_login.lower()), ("enabled", "=", True)]
        )
        if len(keycloak_user) != 1:
            _logger.warning(
                "%d keycloak users found for username %s",
                len(keycloak_user),
                partner_login,
            )
            raise MissingError(_("The given identity is not found!"))
        partner = keycloak_user.partner_id
        if partner.ref != partner_reference:
            _logger.warning(
                "Partner reference does not match: %s != %s for partner %s",
                partner.ref,
                partner_reference,
                partner.name,
            )
            raise MissingError(_("The given identity is not well formatted!"))
        return partner

    def _get_component_context(self):
        ctx = super(
            ShopinvaderAuthApiKeyServiceContextProvider, self
        )._get_component_context()
        shopinvader_partner = self._get_shopinvader_partner()
        authenticated_partner = self._get_authenticated_partner()
        # These keys should never be used....
        ctx["invader_partner"] = shopinvader_partner
        ctx["invader_partner_user"] = shopinvader_partner

        ctx["partner_user"] = authenticated_partner
        ctx["partner"] = authenticated_partner
        return ctx
