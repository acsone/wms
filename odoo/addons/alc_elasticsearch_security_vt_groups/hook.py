# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vt_groups = env["veterinary.group"].search([])
    for vt_group in vt_groups:
        vt_group.delay_create_or_update_linked_role()
