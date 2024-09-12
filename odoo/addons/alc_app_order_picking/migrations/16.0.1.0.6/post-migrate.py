# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _remove_unused_priorities(env):
    """
    Some remaining values are still in ir_model_fields_selection for.

    former stock.move priority field.
    """
    query = """
        DELETE FROM ir_model_fields_selection
            WHERE field_id = (SELECT id FROM ir_model_fields WHERE name = 'priority' AND model = 'stock.move')
            AND value IN ('2', '3')
    """

    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _remove_unused_priorities(env)
