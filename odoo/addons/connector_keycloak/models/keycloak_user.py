# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError
from odoo.osv import expression

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.queue_job.job import identity_exact

from .keycloak_backend import KeycloakBackend


class KeycloakUser(models.Model):

    _name = "keycloak.user"
    _description = "Keycloak User"

    display_name = fields.Char(compute="_compute_display_name")

    keycloak_backend_id = fields.Many2one[KeycloakBackend](
        string="Backend", required=True
    )
    partner_id = fields.Many2one[Partner](string="Partner", required=True)
    username = fields.Char(required=True)
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
            rec.keycloak_username = rec.username.lower()

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            triple_partner = ("partner_id.name", operator, name)
            triple_name = ("username", operator, name)
            op = "&" if operator in expression.NEGATIVE_TERM_OPERATORS else "|"
            domain = [op, triple_name, triple_partner]
        users = self.search(domain + args, limit=limit)
        return users.name_get()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if self.env.context.get("disable_keycloak_sync", False):
            return records
        for rec in records:
            desc = _("Create Keycloak User %(username)s", username=rec.username)
            rec.keycloak_backend_id.with_delay(description=desc).create_user(rec)
        return records

    def unlink(self):
        for user in self:
            desc = _("Delete Keycloak User %(username)s", username=user.username)
            user.keycloak_backend_id.with_delay(description=desc).delete_user(
                user.keycloak_id
            )
        return super().unlink()

    def write(self, vals):
        res = super().write(vals)
        self.check_update_on_keycloak_backend(vals)
        return res

    def check_update_on_keycloak_backend(self, vals):
        if self:  # we need at least one backend
            watched_fields = self[0].keycloak_backend_id._get_update_fields()
            updated_fields = list(set(watched_fields) & set(vals))  # serializable
            if updated_fields:
                self.delay_keycloak_update(list(updated_fields))

    def delay_keycloak_update(self, update_fields=None):
        for user in self:
            user.keycloak_backend_id.with_delay(
                description=_(
                    "Update Keycloak User %(username)s", username=user.username
                ),
                identity_key=identity_exact,  # optimize chained writes
            ).update_user_fields(user, update_fields or [])

    def action_open_update_wizard(self):
        self.ensure_one()
        wizard_model = self.env["keycloak.user.wizard"]
        wizard = wizard_model.create({"keycloak_user_id": self.id})
        action_xml_id = "connector_keycloak.keycloak_user_wizard_action"
        window_action = self.env.ref(action_xml_id).read()[0]
        window_action["res_id"] = wizard.id
        return window_action

    def action_sync_keycloak_info(self):
        if not self.env.user.has_group("connector_keycloak.group_keycloak_manager"):
            raise AccessError(_("You are not allowed to sync keycloak info."))
        updated_fields = self.env["keycloak.backend"]._get_update_fields()
        self.delay_keycloak_update(list(updated_fields))

    def _get_token(self):
        self.ensure_one()
        return self.keycloak_backend_id._get_token(self)

    def _get_payload(self):
        return self.keycloak_backend_id._get_user_payload(self)
