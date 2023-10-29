# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from odoo.addons.base.models.res_partner import Partner

from ..models.keycloak_backend import KeycloakBackend


class KeycloakPartnerWizard(models.TransientModel):
    _name = "keycloak.partner.wizard"
    _description = "Create Keycloak User"

    @api.model
    def _default_backend(self):
        return self.env["keycloak.backend"].search([], limit=1)

    keycloak_backend_id = fields.Many2one[KeycloakBackend](
        default=_default_backend, required=True
    )
    partner_id = fields.Many2one[Partner](string="Partner", required=True)
    username = fields.Char()
    password = fields.Char()
    enabled = fields.Boolean(default=True)

    def execute(self):
        self.ensure_one()
        return self._create_keycloak_user()

    def _get_vals(self):
        return {
            "keycloak_backend_id": self.keycloak_backend_id.id,
            "partner_id": self.partner_id.id,
            "username": self.username,
            "enabled": self.enabled,
        }

    def _create_keycloak_user(self):
        vals = self._get_vals()
        user_model = self.env["keycloak.user"]
        return user_model.with_context(
            test_queue_job_no_delay=True, keycloak_password=self.password
        ).create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "username" not in vals:
                vals["username"] = self.partner_id.browse(vals["partner_id"]).email
        return super().create(vals_list)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        self.ensure_one()
        self.username = self.partner_id.name
