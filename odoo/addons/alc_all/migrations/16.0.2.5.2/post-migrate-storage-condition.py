# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Remove an unwanted condition
    condition = env["stock.storage.location.sequence.cond"].browse(5).exists()
    if condition:
        condition.unlink()
