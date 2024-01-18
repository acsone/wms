# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Upgrade urgent reassorts to priority = "1"
    reassorts = env["stock.picking"].search(
        [
            ("picking_type_id", "in", (14, 13, 37)),
            ("state", "not in", ("done", "cancel")),
            ("group_id.name", "=", "Réassorts urgents"),
        ]
    )
    reassorts.write({"priority": "1"})
