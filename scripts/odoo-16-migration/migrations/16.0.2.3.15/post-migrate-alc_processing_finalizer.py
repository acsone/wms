# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(env):
    # Remove this duplicate that point to the same record
    query = """
        DELETE FROM ir_model_data
            WHERE name = 'mail_template_30'
            AND module = '__export__';
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_data(env)
