# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Convert analytic_policy to property_analytic_policy
    env["account.account"].search(
        [("internal_group", "in", ("income", "expense"))]
    ).write({"analytic_policy": "always"})
    env["account.account"].search(
        [("internal_group", "not in", ("income", "expense"))]
    ).write({"analytic_policy": "optional"})
