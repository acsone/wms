# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set Merge new move for full reassort
    ids = [14, 13, 37]
    env["stock.picking.type"].browse(ids).write(
        {
            "merge_move_for_full_location_reservation": True,
        }
    )
