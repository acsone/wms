# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner

from .keycloak_user import KeycloakUser


class ResPartner(Partner):

    keycloak_user_ids = fields.One2many[KeycloakUser](
        inverse_name="partner_id", string="Keycloak Users", copy=False
    )

    def write(self, vals):
        res = super().write(vals)
        self.sudo().keycloak_user_ids.check_update_on_keycloak_backend(vals)
        return res

    def action_create_keycloak_user(self):
        self.ensure_one()
        wizard_model = self.env["keycloak.partner.wizard"]
        wizard = wizard_model.create({"partner_id": self.id})
        action_xml_id = "keycloak.keycloak_partner_wizard_action"
        window_action = self.env.ref(action_xml_id).read()[0]
        window_action["res_id"] = wizard.id
        return window_action
