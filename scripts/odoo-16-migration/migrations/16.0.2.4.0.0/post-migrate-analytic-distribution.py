# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_analytic(env):
    """Some analytic distributions are not well migrated (account 282 is correct)."""

    query = """

        UPDATE account_move_line
            SET analytic_distribution = '{"282": 100}'
            WHERE analytic_distribution::TEXT LIKE '{"282": 100,% 100%';
    """

    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_analytic(env)
