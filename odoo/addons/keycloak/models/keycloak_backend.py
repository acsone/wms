# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import keycloak

from odoo import api, fields
from odoo.models import Model


class KeycloakBackend(Model):

    _name = "keycloak.backend"
    _description = "Keycloak Backend"
    _inherit = "server.env.mixin"

    name = fields.Char()
    server_url = fields.Char()
    client_id = fields.Char(string="Client", help="Client to create users.")
    realm_name = fields.Char()
    client_secret_key = fields.Char()
    user_realm_name = fields.Char()

    @property
    def _server_env_fields(self):
        env_fields = super()._server_env_fields
        new = {
            "server_url": {},
            "client_id": {},
            "realm_name": {},
            "client_secret_key": {},
            "user_realm_name": {},
        }
        env_fields.update(new)
        return env_fields

    def _get_admin_client(self):
        """The client should be defined on the master realm to perform admin tasks."""
        self.ensure_one()
        return keycloak.KeycloakAdmin(
            server_url=self.server_url,
            client_id=self.client_id,
            client_secret_key=self.client_secret_key,
            realm_name=self.realm_name,
            user_realm_name=self.realm_name,
        )

    def _get_openid_client(self):
        """The client should be defined on the target realm."""
        self.ensure_one()
        params = {
            "server_url": self.server_url,
            "client_id": self.realm_client_id,
            "realm_name": self.realm_name,
            "client_secret_key": self.realm_client_secret_key,
        }
        return keycloak.KeycloakOpenID(**params)

    def _get_user_token(self, keycloak_user):
        username = keycloak_user.keycloak_username
        return self._get_token_from_user_info(username, keycloak_user.password)

    def _get_token_from_user_info(self, username, password):
        return self._get_openid_client().token(username, password)

    def create_user(self, keycloak_user):
        self.ensure_one()
        payload = self._keycloak_user_to_payload(keycloak_user)
        client = self._get_admin_client()
        keycloak_id = client.create_user(payload, exist_ok=True)
        keycloak_user.keycloak_id = keycloak_id
        return keycloak_id

    @api.model
    def _keycloak_user_to_payload(self, keycloak_user):
        """Extract fields from the user and the partner.

        To register custom attributes, override this with _get_update_fields
        to keep them in sync.
        """
        keycloak_user.ensure_one()
        split_name = keycloak_user.partner_id.name.split(None, 1)
        payload = {
            "email": keycloak_user.partner_id.email,
            "username": keycloak_user.keycloak_username,
            "enabled": keycloak_user.enabled,
            "firstName": split_name[0] if len(split_name) > 0 else "",
            "lastName": split_name[1] if len(split_name) > 1 else "",
            "attributes": {},
        }
        keycloak_password = self.env.context.get("keycloak_password", None)
        if keycloak_password:
            payload["credentials"] = [{"value": keycloak_password, "type": "password"}]
        return payload

    def delete_user(self, keycloak_id):
        self.ensure_one()
        client = self._get_admin_client()
        return client.delete_user(user_id=keycloak_id)

    def update_user_password(self, user, password, temporary=True):
        client = self._get_admin_client()
        return client.set_user_password(
            user_id=user.keycloak_id, password=password, temporary=temporary
        )

    @api.model
    def _get_update_fields(self):
        """A dictionary of fields that, if updated, trigger an update on Keycloak.

        The value, if different, is the field name in the keycloak payload:
        "custom_field": "keycloak-custom-name"
        Note that the fields may either be on keycloak.user or res.partner.
        Note also that by simplicity this list is for all backends.
        If the backend is configured to 'login with email', username is tacitly
        ignored if email is set (without triggering any error).
        In that case, there's implicitly a unicity constraint on the email field.
        Password is omitted as it should only be updated through the wizard.
        Name is a special case, since it updates first and last name.
        """
        return {
            "username": "username",
            "enabled": "enabled",
            "email": "email",
            "name": None,
        }

    def _filter_payload_fields(self, payload, updated_fields):
        # do we really need to filter everything out?
        base_fields_to_keep = {"email", "enabled", "username"} & set(updated_fields)
        if "name" in updated_fields:
            base_fields_to_keep |= {"firstName", "lastName"}
        result = {f: payload[f] for f in base_fields_to_keep}
        update_fields = self._get_update_fields()
        # if an attribute is updated, we must provides all the attributes
        attrs = payload["attributes"]
        attributes_to_keep = {update_fields[f] for f in updated_fields}
        updated_attributes = {a: attrs[a] for a in attributes_to_keep if a in attrs}
        if updated_attributes:
            result["attributes"] = attrs
        return result

    def update_user_fields(self, user, updated_fields):
        client = self._get_admin_client()
        payload = self._get_user_payload(user, updated_fields)
        return client.update_user(user_id=user.keycloak_id, payload=payload)

    def _get_user_payload(self, user, updated_fields=None):
        updated_fields = updated_fields or self._get_update_fields().keys()
        payload_all = self._keycloak_user_to_payload(user)
        return self._filter_payload_fields(payload_all, updated_fields)

    @api.model
    def _get_available_actions(self):
        """The list of actions we can ask Keycloak to perform."""
        return [
            "UPDATE_PASSWORD",
            "VERIFY_EMAIL",
            "UPDATE_PROFILE",
            "terms_and_conditions",
            "CONFIGURE_TOTP",
            "update_user_locale",
            "delete_account",
        ]

    def send_user_action(self, user, action):
        client = self._get_admin_client()
        return client.send_update_account(user_id=user.keycloak_id, payload=[action])
