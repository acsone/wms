# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import identity_exact


class KeycloakUser(models.Model):

    _name = "keycloak.user"
    _description = "Keycloak User"

    display_name = fields.Char(compute="_compute_display_name")

    keycloak_backend_id = fields.Many2one(
        "keycloak.backend", string="Backend", required=True
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    username = fields.Char()
    keycloak_username = fields.Char(
        compute="_compute_keycloak_username",
        store=True,
        help="In keycloak, username is stored in lowercase. The username is "
        "also case insensitive into the login form. Nevertheless, "
        "the information into the token is always lower case. To ease the"
        "matching between the token and keycloak.user, we also store"
        "the username in lower case into a dedicated column.",
    )
    enabled = fields.Boolean(default=True)

    keycloak_id = fields.Char(readonly=True)

    _sql_constraints = [
        (
            "backend_partner_uniq",
            "unique(keycloak_backend_id, partner_id)",
            _("This partner already has a user on this backend."),
        ),
        (
            "backend_keycloak_id_uniq",
            "unique(keycloak_backend_id, keycloak_id)",
            _("This Keycloak ID already exists, which should be impossible."),
        ),
        (
            "backend_keycloak_username_unique",
            "unique(keycloak_backend_id, keycloak_username)",
            _("This username already exists on this backend"),
        ),
    ]

    @api.depends("username", "partner_id.name")
    def _compute_display_name(self):
        for u in self:
            u.display_name = u.username + " (" + (u.partner_id.name or "") + ")"

    @api.depends("username")
    def _compute_keycloak_username(self):
        for rec in self:
            username = rec.username or ""
            rec.keycloak_username = username.lower()

    @api.model
    def create(self, vals):
        res = super(KeycloakUser, self).create(vals)
        if not self.env.context.get("disable_keycloak_sync", False):
            desc = _("Create Keycloak User %s") % res.username
            res.keycloak_backend_id.with_delay(description=desc).create_user(res)
        return res

    def unlink(self):
        for user in self:
            desc = _("Delete Keycloak User %s") % user.username
            user.keycloak_backend_id.with_delay(description=desc).delete_user(user)
        return super(KeycloakUser, self).unlink()

    def write(self, vals):
        res = super(KeycloakUser, self).write(vals)
        self.check_update_on_keycloak_backend(vals)
        return res

    def check_update_on_keycloak_backend(self, vals):
        if self:  # we need at least one backend
            watched_fields = self[0].keycloak_backend_id._get_update_fields()
            updated_fields = list(set(watched_fields) & set(vals))  # serializable
            if updated_fields:
                for user in self:
                    user.keycloak_backend_id.with_delay(
                        description=_("Update Keycloak User %s") % user.username,
                        identity_key=identity_exact,  # optimize chained writes
                    ).update_user_fields(user, list(updated_fields))

    def action_open_update_wizard(self):
        self.ensure_one()
        wizard_model = self.env["keycloak.user.wizard"]
        wizard = wizard_model.create({"keycloak_user_id": self.id})
        action_xml_id = "keycloak.keycloak_user_wizard_action"
        window_action = self.env.ref(action_xml_id).read()[0]
        window_action["res_id"] = wizard.id
        return window_action

    def _get_token(self):
        self.ensure_one()
        return self.keycloak_backend_id._get_token(self)
