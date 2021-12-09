# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class KeycloakUser(models.Model):

    _inherit = "keycloak.user"

    elasticsearch_role = fields.Char(
        related="partner_id.elasticsearch_role", store=True
    )
