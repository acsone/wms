# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MagentoUser(models.Model):

    _name = "magento.user"
    _description = "Magento User"

    username = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    magento_id = fields.Char(required=True)
    activated = fields.Boolean(default=False)

    def _to_keycloak_user_payload(self):
        """Create keycloak user payload by using a temporary in memory keycloak
        user."""
        self.ensure_one()
        keycloak_user = self.env["keycloak.user"].new(
            {"partner_id": self.partner_id, "username": self.username}
        )
        payload = self.env["keycloak.backend"]._keycloak_user_to_payload(keycloak_user)
        payload.pop("credentials", None)
        payload.update({"id": self.magento_id, "enabled": True, "emailVerified": True})
        # attribute values are expected to be a list of string by the caller
        attributes = payload["attributes"]
        new_attr = {}
        for attr, value in attributes.items():
            new_attr[attr] = [value]
        payload["attributes"] = new_attr
        return payload

    def _finalize_registration(self):
        """Finalize the user registration on keycloak.

        * Create the keycloak user
        * Mark the record has activated
        """
        self.ensure_one()
        self.activated = True
        return (
            self.env["keycloak.user"]
            .with_context(disable_keycloak_sync=True)
            .create(
                {
                    "username": self.username,
                    "keycloak_id": self.magento_id,
                    "partner_id": self.partner_id.id,
                    "keycloak_backend_id": self.env.ref("keycloak.keycloak_backend").id,
                }
            )
        )
