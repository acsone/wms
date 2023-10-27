# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=odoo-addons-relative-import
# pylint: disable=cyclic-import
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

from odoo.addons.keycloak.models.keycloak_user import KeycloakUser


class KeycloakPartnerWizard(models.TransientModel):
    _name = "keycloak.user.wizard"
    _description = "Update Keycloak User"

    @api.model
    def _get_action_selection(self):
        return [(a, a) for a in self.env["keycloak.backend"]._get_available_actions()]

    @api.model
    def _get_default_action(self):
        return self._get_action_selection()[0][0]

    keycloak_user_id = fields.Many2one[KeycloakUser](
        required=True, readonly=True, ondelete="cascade"
    )
    password = fields.Char()
    temporary = fields.Boolean(default=True)
    type = fields.Selection(
        required=True,
        default="password",
        selection=[("action", "action"), ("password", "password")],
    )
    action = fields.Selection(
        default=_get_default_action,
        selection=_get_action_selection,
    )

    def execute(self):
        if not self.env.user.has_group("keycloak.group_keycloak_manager"):
            raise AccessError(_("You are not allowed to update keycloak user."))
        self.ensure_one()
        if self.type == "password":
            return self._update_password()
        if self.type == "action":
            return self._send_user_action()
        return None  # safer in case of override, and keep pylint happy

    def _send_user_action(self):
        user = self.keycloak_user_id
        return user.keycloak_backend_id.send_user_action(user, self.action)

    def _update_password(self):
        user = self.keycloak_user_id
        if not self.password:
            raise ValidationError(_("You need to enter a password."))
        return user.keycloak_backend_id.update_user_password(
            user, self.password, self.temporary
        )
