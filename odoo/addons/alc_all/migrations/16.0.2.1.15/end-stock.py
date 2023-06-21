# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _move_aliment(env):
    """Move the Aliments location under Stock."""
    aliment = env["stock.location"].browse(23)
    aliment.write({"location_id": 15})


@openupgrade.migrate()
def migrate(env, version):
    _move_aliment(env)
