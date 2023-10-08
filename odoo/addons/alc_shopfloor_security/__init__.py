# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def _post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    group = env.ref("alc_shopfloor_security.alc_shopfloor_portal_user")
    for user in env["auth.api.key"].search([]).shopfloor_user_id:
        user.groups_id += group
