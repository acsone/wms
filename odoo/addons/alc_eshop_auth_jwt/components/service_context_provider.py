# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ShopinvaderAuthJwtServiceContextProvider(Component):
    _inherit = [
        "auth_jwt.shopinvader.service.context.provider",
        "abstract.auth.jwt.authenticated.partner.provider",
    ]

    _name = "auth_jwt.shopinvader.service.context.provider"

    def _get_shopinvader_partner(self):
        # disable useless shopinvader partner
        return self.env["shopinvader.partner"].browse()

    def _get_backend(self):
        backend = super(ShopinvaderAuthJwtServiceContextProvider, self)._get_backend()
        if self._jwt_payload:
            # no jwt_payload = public services...
            audience = self._jwt_payload.get("aud")
            backend_model = self.env["shopinvader.backend"]
            if backend:
                # validate that this backend can be used for the aud
                backend = backend if backend.jwt_aud == audience else backend_model
                if not backend:
                    _logger.warning(
                        "Audience inconsistency for between provided backend and "
                        "jwt toeken: Backend %s (%s != %s)",
                        backend.name,
                        backend.jwt_aud,
                        audience,
                    )
                    return backend
            return backend_model._get_from_jwt_aud(self.request.jwt_payload.get("aud"))
        return backend

    def _get_component_context(self):
        ctx = super(
            ShopinvaderAuthJwtServiceContextProvider, self
        )._get_component_context()
        shopinvader_partner = self._get_shopinvader_partner()
        authenticated_partner = self.env["res.partner"].browse()
        authenticated_partner_id = self._get_authenticated_partner_id()
        if authenticated_partner_id:
            authenticated_partner = self.env["res.partner"].browse(
                authenticated_partner_id
            )
        # These keys should never be used....
        ctx["invader_partner"] = shopinvader_partner
        ctx["invader_partner_user"] = shopinvader_partner

        ctx["partner_user"] = authenticated_partner
        ctx["partner"] = authenticated_partner
        return ctx
