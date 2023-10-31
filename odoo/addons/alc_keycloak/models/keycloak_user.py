# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.connector_keycloak.models.keycloak_user import (
    KeycloakUser as KeycloakUserBase,
)


class KeycloakUser(KeycloakUserBase):

    elasticsearch_role = fields.Char(related="partner_id.elasticsearch_role")
