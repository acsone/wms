# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    action = env["ir.actions.server"].search(
        [("name", "=", "Price Cache Recompute"), ("state", "=", "code")]
    )
    if not action:
        return
    action.code = action.code.replace(".update_price_cache", "._update_price_cache")
