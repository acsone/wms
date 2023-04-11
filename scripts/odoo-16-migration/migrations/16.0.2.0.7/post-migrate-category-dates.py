# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _move_column(env):
    """
    Move life_time field values to expiration_time.

    The other fields are normally automatically updated (on xmlid side) by Odoo
    during update process
    """
    if openupgrade.column_exists(env.cr, "product_category", "life_time"):
        query = """
            UPDATE product_category
                SET expiration_time = life_time
                WHERE life_time <> 0
        """
        openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _move_column(env)
