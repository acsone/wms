# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Change some particular routes to 'Release based on Available to Promise'."""
    ids = [9, 11, 13, 14, 20]
    env["stock.route"].browse(ids).exists().write(
        {"available_to_promise_defer_pull": True}
    )
