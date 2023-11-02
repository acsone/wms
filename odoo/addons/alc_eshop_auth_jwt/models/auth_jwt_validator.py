# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields

from odoo.addons.auth_jwt.models import auth_jwt_validator

_logger = logging.getLogger(__name__)


class AuthJwtValidator(auth_jwt_validator.AuthJwtValidator):

    partner_id_strategy = fields.Selection(
        selection_add=[("keycloak_pref_user", "Keycloak User")]
    )

    def _get_partner_id(self, payload):
        # override for additional strategies
        if self.partner_id_strategy == "keycloak_pref_user":
            username = payload.get("preferred_username")
            if not username:
                _logger.debug("JWT payload does not have a preferred_username claim")
                return None
            keycloak_user = self.env["keycloak.user"].search(
                [("keycloak_username", "=", username), ("enabled", "=", True)]
            )
            if len(keycloak_user) != 1:
                _logger.debug(
                    "%d keycloak users found for username %s",
                    len(keycloak_user),
                    username,
                )
                return None
            return keycloak_user.partner_id.id
        return super()._get_partner_id(payload)
