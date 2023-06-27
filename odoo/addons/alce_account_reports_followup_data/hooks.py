# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def _delete_demo_data(env):
    """To avoid sql constraint conflicts."""
    env["account_followup.followup.line"].search(
        [
            ("delay", "in", (15, 30, 40)),
            ("company_id", "=", env.ref("base.main_company").id),
        ]
    ).unlink()


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _delete_demo_data(env)
