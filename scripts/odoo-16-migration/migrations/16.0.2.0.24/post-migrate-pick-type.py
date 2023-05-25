# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Change some properties on Reception picking type."""
    ids = [1]
    env["stock.picking.type"].browse(ids).exists().write(
        {
            "use_create_lots": True,
            "is_grn_mandatory": True,
        }
    )
